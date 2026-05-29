const $ = (id) => document.getElementById(id);

const el = {
  filePath: $("filePath"),
  filePill: $("filePill"),
  bands: $("bands"),
  headerOffset: $("headerOffset"),
  height: $("height"),
  width: $("width"),
  bandIndex: $("bandIndex"),
  pixelX: $("pixelX"),
  pixelY: $("pixelY"),
  bandImg: $("bandImg"),
  specImg: $("specImg"),
  bandPlaceholder: $("bandPlaceholder"),
  specPlaceholder: $("specPlaceholder"),
  bandMeta: $("bandMeta"),
  specMeta: $("specMeta"),
  fileList: $("fileList"),
  log: $("log"),
  status: $("status"),
};

const state = { hsiPath: null, outputDir: null };

function setStatus(msg, kind = "ok") {
  el.status.textContent = msg;
  el.status.className =
    kind === "bad" ? "status-bad" : kind === "good" ? "status-good" : "status-ok";
}
const num = (node) => parseInt(node.value, 10);
const basename = (p) => (p ? p.split(/[\\/]/).pop() : "");

// ---------------------------------------------------------------------------
// Wybór pliku
// ---------------------------------------------------------------------------
$("btnPickHsi").addEventListener("click", async () => {
  const p = await window.hsi.pickHsi();
  if (!p) return;
  state.hsiPath = p;
  el.filePath.textContent = p;
  el.filePill.textContent = basename(p);
  setStatus("Wybrano plik. Ustaw parametry i kliknij „Uruchom”.");
});

// ---------------------------------------------------------------------------
// Uruchomienie
// ---------------------------------------------------------------------------
$("btnRun").addEventListener("click", async () => {
  if (!state.hsiPath) return setStatus("Najpierw wybierz plik .HSI.", "bad");

  const params = {
    filePath: state.hsiPath,
    bands: num(el.bands),
    height: num(el.height),
    width: num(el.width),
    headerOffset: num(el.headerOffset),
    bandIndex: num(el.bandIndex),
    pixelX: num(el.pixelX),
    pixelY: num(el.pixelY),
  };

  if ([params.bands, params.height, params.width, params.headerOffset,
       params.bandIndex, params.pixelX, params.pixelY].some(Number.isNaN)) {
    return setStatus("Wszystkie parametry liczbowe muszą być wypełnione.", "bad");
  }

  setStatus("Przetwarzanie…");
  el.log.textContent = "Trwa wykonywanie…";
  $("btnRun").disabled = true;

  let res;
  try {
    res = await window.hsi.runPipeline(params);
  } catch (e) {
    $("btnRun").disabled = false;
    return setStatus("Błąd komunikacji: " + e.message, "bad");
  }
  $("btnRun").disabled = false;

  el.log.textContent = res.log && res.log.trim() ? res.log : "(brak wyjścia)";

  if (!res.ok) {
    clearResults();
    setStatus(res.error || "Przetwarzanie zakończyło się błędem.", "bad");
    return;
  }

  if (res.bandImage) {
    el.bandImg.src = res.bandImage;
    el.bandImg.style.display = "block";
    el.bandPlaceholder.style.display = "none";
    el.bandMeta.textContent = `pasmo ${params.bandIndex}`;
  }
  if (res.specImage) {
    el.specImg.src = res.specImage;
    el.specImg.style.display = "block";
    el.specPlaceholder.style.display = "none";
    el.specMeta.textContent = `pixel_X${params.pixelX}_Y${params.pixelY}`;
  }

  state.outputDir = res.outputDir;
  renderFileList(res.files);
  $("btnOpenDir").disabled = false;
  setStatus("Gotowe — pliki zapisane w folderze „plots”.", "good");
});

// ---------------------------------------------------------------------------
// Lista zapisanych plików
// ---------------------------------------------------------------------------
function renderFileList(files) {
  const order = [
    ["bandPng", "Obraz pasma (PNG)"],
    ["specPng", "Profil widmowy (PNG)"],
    ["bandJson", "Pasmo (JSON)"],
    ["specCsv", "Widmo (CSV)"],
    ["specJson", "Widmo (JSON)"],
  ];
  el.fileList.innerHTML = "";
  for (const [key, label] of order) {
    const p = files[key];
    const li = document.createElement("li");

    const meta = document.createElement("div");
    meta.className = "file-meta";
    meta.innerHTML = `<span class="file-label">${label}</span><span class="file-name">${basename(p)}</span>`;

    const actions = document.createElement("div");
    actions.className = "file-actions";
    const openBtn = document.createElement("button");
    openBtn.className = "btn btn-ghost mini";
    openBtn.textContent = "Otwórz";
    openBtn.addEventListener("click", async () => {
      const errMsg = await window.hsi.openPath(p);
      if (errMsg) setStatus("Nie udało się otworzyć pliku: " + errMsg, "bad");
    });
    const showBtn = document.createElement("button");
    showBtn.className = "btn btn-ghost mini";
    showBtn.textContent = "Pokaż w folderze";
    showBtn.addEventListener("click", () => window.hsi.showInFolder(p));

    actions.append(openBtn, showBtn);
    li.append(meta, actions);
    el.fileList.append(li);
  }
}

function clearResults() {
  el.bandImg.style.display = "none";
  el.specImg.style.display = "none";
  el.bandPlaceholder.style.display = "block";
  el.specPlaceholder.style.display = "block";
  el.bandMeta.textContent = "—";
  el.specMeta.textContent = "—";
  el.fileList.innerHTML = '<li class="muted">Brak — uruchom przetwarzanie.</li>';
  $("btnOpenDir").disabled = true;
}

$("btnOpenDir").addEventListener("click", async () => {
  if (!state.outputDir) return;
  const errMsg = await window.hsi.openPath(state.outputDir);
  if (errMsg) setStatus("Nie udało się otworzyć folderu: " + errMsg, "bad");
});
