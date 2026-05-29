const { app, BrowserWindow, ipcMain, dialog, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1240,
    height: 900,
    minWidth: 960,
    minHeight: 700,
    backgroundColor: "#0e1116",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  mainWindow.loadFile("index.html");
  // mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

function resolveBackend() {
  const exeName = process.platform === "win32" ? "HSI_encoder.exe" : "HSI_encoder";

  // 1) Wersja spakowana: zamrożony backend w zasobach aplikacji.
  if (app.isPackaged) {
    const cmd = path.join(process.resourcesPath, "python", exeName);
    return { cmd, baseArgs: [], cwd: path.dirname(cmd), mode: "frozen" };
  }

  const devFrozen = path.join(__dirname, "resources", "python", exeName);
  if (fs.existsSync(devFrozen)) {
    return { cmd: devFrozen, baseArgs: [], cwd: path.dirname(devFrozen), mode: "frozen" };
  }

  const scriptPath = path.resolve(path.join(__dirname, "..", "HSI_encoder.py"));
  const projectRoot = path.dirname(scriptPath);
  const winVenv = path.join(projectRoot, ".venv", "Scripts", "python.exe");
  const posixVenv = path.join(projectRoot, ".venv", "bin", "python");

  let py;
  if (process.platform === "win32" && fs.existsSync(winVenv)) py = winVenv;
  else if (fs.existsSync(posixVenv)) py = posixVenv;
  else py = process.platform === "win32" ? "python" : "python3";

  return { cmd: py, baseArgs: [scriptPath], cwd: projectRoot, mode: "script", scriptPath };
}

function pngToDataUrl(p) {
  try {
    return "data:image/png;base64," + fs.readFileSync(p).toString("base64");
  } catch {
    return null;
  }
}

ipcMain.handle("pick-hsi", async () => {
  const r = await dialog.showOpenDialog(mainWindow, {
    title: "Wybierz plik .HSI",
    properties: ["openFile"],
    filters: [
      { name: "Pliki HSI", extensions: ["HSI", "hsi"] },
      { name: "Wszystkie pliki", extensions: ["*"] },
    ],
  });
  return r.canceled || !r.filePaths.length ? null : r.filePaths[0];
});

ipcMain.handle("open-path", async (_e, p) => (p ? await shell.openPath(p) : "Brak ścieżki."));
ipcMain.handle("show-in-folder", async (_e, p) => {
  if (p) shell.showItemInFolder(p);
  return null;
});

ipcMain.handle("run-pipeline", (_e, p) =>
  new Promise((resolve) => {
    if (!p.filePath) return resolve({ ok: false, error: "Najpierw wybierz plik .HSI.", log: "" });
    if (!fs.existsSync(p.filePath)) {
      return resolve({ ok: false, error: `Nie znaleziono pliku .HSI: ${p.filePath}`, log: "" });
    }

    const backend = resolveBackend();

    if (backend.mode === "frozen" && !fs.existsSync(backend.cmd)) {
      return resolve({
        ok: false,
        error:
          "Nie znaleziono dołączonego backendu:\n" +
          backend.cmd +
          "\nUpewnij się, że zamrożony plik HSI_encoder(.exe) został dołączony do aplikacji.",
        log: "",
      });
    }

    const args = [
      ...backend.baseArgs,
      "--file-path", p.filePath,
      "--bands", String(p.bands),
      "--height", String(p.height),
      "--width", String(p.width),
      "--header-offset", String(p.headerOffset),
      "--band-index", String(p.bandIndex),
      "--pixel-x", String(p.pixelX),
      "--pixel-y", String(p.pixelY),
      "--no-display",
    ];

    const env = { ...process.env, MPLBACKEND: "Agg", PYTHONIOENCODING: "utf-8" };

    let child;
    try {
      child = spawn(backend.cmd, args, { cwd: backend.cwd, env, windowsHide: true });
    } catch (e) {
      return resolve({ ok: false, error: "Nie udało się uruchomić backendu: " + e.message, log: "" });
    }

    let out = "";
    let errOut = "";
    let settled = false;

    child.stdout.on("data", (d) => (out += d.toString("utf-8")));
    child.stderr.on("data", (d) => (errOut += d.toString("utf-8")));

    child.on("error", (e) => {
      if (settled) return;
      settled = true;
      const hint =
        backend.mode === "script"
          ? " Sprawdź, czy Python z zależnościami (numpy/pandas/matplotlib) jest dostępny."
          : "";
      resolve({ ok: false, error: "Nie udało się uruchomić backendu (" + e.message + ")." + hint, log: out + errOut });
    });

    child.on("close", (code) => {
      if (settled) return;
      settled = true;

      const outputDir = path.join(path.dirname(p.filePath), "plots");
      const baseName = path.parse(p.filePath).name;
      const files = {
        bandPng: path.join(outputDir, `${baseName}_band_${p.bandIndex}.png`),
        bandJson: path.join(outputDir, `${baseName}_band_${p.bandIndex}.json`),
        specPng: path.join(outputDir, `${baseName}_${p.pixelX}_${p.pixelY}_spectrum.png`),
        specCsv: path.join(outputDir, `${baseName}_${p.pixelX}_${p.pixelY}_spectrum.csv`),
        specJson: path.join(outputDir, `${baseName}_${p.pixelX}_${p.pixelY}_spectrum.json`),
      };

      const ok = code === 0 && fs.existsSync(files.bandPng);
      const log = out + (errOut ? "\n[stderr]\n" + errOut : "");

      resolve({
        ok,
        code,
        log,
        error: ok ? null : "Pipeline nie wygenerował obrazów — sprawdź log poniżej.",
        outputDir,
        files,
        bandImage: pngToDataUrl(files.bandPng),
        specImage: pngToDataUrl(files.specPng),
      });
    });
  })
);
