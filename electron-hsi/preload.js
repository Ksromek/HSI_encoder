const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("hsi", {
  pickHsi: () => ipcRenderer.invoke("pick-hsi"),
  runPipeline: (params) => ipcRenderer.invoke("run-pipeline", params),
  openPath: (p) => ipcRenderer.invoke("open-path", p),
  showInFolder: (p) => ipcRenderer.invoke("show-in-folder", p),
});
