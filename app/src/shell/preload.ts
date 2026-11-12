import { contextBridge, ipcRenderer } from 'electron'

import type { TraceBridge } from '../bridge'

const bridge: TraceBridge = {
  coreConnection: () => ipcRenderer.invoke('trace:core-connection'),
  chooseLogFile: () => ipcRenderer.invoke('trace:choose-log-file'),
}

contextBridge.exposeInMainWorld('trace', bridge)
