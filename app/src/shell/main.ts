import { randomBytes } from 'node:crypto'
import { join, sep } from 'node:path'
import { pathToFileURL } from 'node:url'

import { app, BrowserWindow, dialog, ipcMain, net, protocol } from 'electron'
import type { IpcMainInvokeEvent } from 'electron'

import type { CoreConnection } from '../bridge'
import { startCore, type Core } from './core-process'

// Tests, and anyone who wants a library apart from their real one, can keep
// all of the application's data in a folder of their choosing.
if (process.env.TRACE_USER_DATA_DIR) {
  app.setPath('userData', process.env.TRACE_USER_DATA_DIR)
}

// Where the window loads the user interface from: the development server
// while working on it (`npm run dev`), otherwise the built files, served
// under a scheme of TRACE's own so that the page has a proper web origin.
const UI_SCHEME = 'trace'
const devServerUrl = process.env.ELECTRON_RENDERER_URL
const ui = devServerUrl
  ? { url: devServerUrl, origin: new URL(devServerUrl).origin }
  : { url: `${UI_SCHEME}://ui/`, origin: `${UI_SCHEME}://ui` }

protocol.registerSchemesAsPrivileged([
  { scheme: UI_SCHEME, privileges: { standard: true, secure: true, supportFetchAPI: true } },
])

/** A new secret at every launch; only the core and the user interface are given it. */
const secret = randomBytes(32).toString('hex')
let core: Core | undefined

function serveBuiltUi(): void {
  const root = join(__dirname, '..', 'ui')
  protocol.handle(UI_SCHEME, (request) => {
    const path = decodeURIComponent(new URL(request.url).pathname)
    const file = join(root, path === '/' ? 'index.html' : path)
    if (!file.startsWith(root + sep)) {
      return new Response(null, { status: 404 })
    }
    return net.fetch(pathToFileURL(file).toString())
  })
}

/** How to run the core from source: with the Python environment uv keeps in core/. */
function coreCommand(): { command: string; args: string[] } {
  const environment = join(app.getAppPath(), '..', 'core', '.venv')
  const python =
    process.platform === 'win32'
      ? join(environment, 'Scripts', 'python.exe')
      : join(environment, 'bin', 'python')
  return { command: python, args: ['-m', 'trace_telemetry'] }
}

/** Only the user interface itself may use the bridge. */
function fromUi(event: IpcMainInvokeEvent): boolean {
  return event.senderFrame?.url.startsWith(ui.url) ?? false
}

function offerBridge(): void {
  ipcMain.handle('trace:core-connection', async (event): Promise<CoreConnection> => {
    if (!fromUi(event) || !core) throw new Error('Not available.')
    return { baseUrl: await core.ready, secret }
  })

  ipcMain.handle('trace:choose-log-file', async (event): Promise<string | null> => {
    const window = BrowserWindow.fromWebContents(event.sender)
    if (!fromUi(event) || !window) throw new Error('Not available.')
    const chosen = await dialog.showOpenDialog(window, {
      title: 'Import Log',
      properties: ['openFile'],
      filters: [{ name: 'Racelogic VBOX', extensions: ['vbo'] }],
    })
    return chosen.canceled ? null : (chosen.filePaths[0] ?? null)
  })
}

function openWindow(): void {
  const window = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1280,
    minHeight: 720,
    title: 'TRACE Telemetry',
    webPreferences: {
      preload: join(__dirname, '..', 'preload', 'preload.js'),
      sandbox: true,
      contextIsolation: true,
      nodeIntegration: false,
    },
  })
  // The window shows the user interface and nothing else.
  window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }))
  window.webContents.on('will-navigate', (event) => event.preventDefault())
  void window.loadURL(ui.url)
}

void app.whenReady().then(() => {
  if (!devServerUrl) serveBuiltUi()

  core = startCore({
    ...coreCommand(),
    dataDir: join(app.getPath('userData'), 'library'),
    secret,
    uiOrigin: ui.origin,
  })
  // The user interface is told when it asks for the connection; this only
  // leaves a trace for whoever started the application from a terminal.
  core.ready.catch((cause: Error) => console.error(cause.message))

  offerBridge()
  openWindow()
})

app.on('window-all-closed', () => app.quit())
app.on('will-quit', () => core?.stop())
