import { execFileSync } from 'node:child_process'
import { mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

import { _electron as electron, expect, test, type ElectronApplication } from '@playwright/test'

const appFolder = resolve(__dirname, '..')
const coreFolder = resolve(appFolder, '..', 'core')

let scratch: string
let userData: string

test.beforeEach(() => {
  scratch = mkdtempSync(join(tmpdir(), 'trace-e2e-'))
  userData = join(scratch, 'user-data')
})

test.afterEach(() => {
  rmSync(scratch, { recursive: true, force: true })
})

/** Starts the application from source, keeping its data in a folder of the test's own. */
function launch(): Promise<ElectronApplication> {
  return electron.launch({
    args: [appFolder],
    env: { ...process.env, TRACE_USER_DATA_DIR: userData },
  })
}

/** Writes the synthetic car `.vbo` fixture with the core's fixture generator. */
function writeCarFixture(): string {
  const file = join(scratch, 'car-circuit.vbo')
  execFileSync('uv', [
    'run',
    '--project',
    coreFolder,
    'python',
    join(coreFolder, 'tests', 'synthetic_vbo.py'),
    file,
  ])
  return file
}

/**
 * The file dialog is the operating system's own, so the test answers for the
 * user: the next dialog "chooses" this file, and what it was asked is noted.
 */
async function answerFileDialogWith(app: ElectronApplication, file: string): Promise<void> {
  await app.evaluate(({ dialog }, chosen) => {
    dialog.showOpenDialog = (async (...asked: unknown[]) => {
      ;(globalThis as Record<string, unknown>).askedOfDialog = asked.at(-1)
      return { canceled: false, filePaths: [chosen] }
    }) as typeof dialog.showOpenDialog
  }, file)
}

test('a .vbo imported through the file dialog is in the library, and still there after a restart', async () => {
  const fixture = writeCarFixture()

  // Starting the application opens a window and starts the core: the library
  // can only say it is empty once the core has answered.
  let app = await launch()
  let page = await app.firstWindow()
  await expect(page.getByRole('heading', { name: 'Library' })).toBeVisible()
  await expect(page.getByText('No Logs yet')).toBeVisible()

  await answerFileDialogWith(app, fixture)
  await page.getByRole('button', { name: 'Import Log' }).click()

  const logs = page.getByRole('list', { name: 'Logs' })
  await expect(logs.getByRole('listitem')).toHaveCount(1)
  await expect(logs.getByRole('listitem')).toContainText('car-circuit.vbo')
  const asked = await app.evaluate(() => (globalThis as Record<string, unknown>).askedOfDialog)
  expect(asked).toMatchObject({ filters: [{ extensions: ['vbo'] }] })

  // The Log is kept in the application's data folder: its Channel data as
  // Parquet, and the imported file beside it, unchanged.
  const logsFolder = join(userData, 'library', 'logs')
  const [logFolder] = readdirSync(logsFolder)
  const kept = readFileSync(join(logsFolder, logFolder, 'original', 'car-circuit.vbo'))
  expect(kept.equals(readFileSync(fixture))).toBe(true)
  const channelFiles = readdirSync(join(logsFolder, logFolder, 'outing-1'))
  expect(channelFiles.length).toBeGreaterThan(0)
  expect(channelFiles.every((name) => name.endsWith('.parquet'))).toBe(true)

  // The core's API turns away a caller without the secret of this launch.
  const core = await page.evaluate(() => window.trace.coreConnection())
  expect((await fetch(`${core.baseUrl}/logs`)).status).toBe(401)

  // Quitting the application stops the core.
  await app.close()
  await expect(async () => {
    await expect(fetch(`${core.baseUrl}/logs`)).rejects.toThrow()
  }).toPass({ timeout: 10_000 })

  // After a restart the Log is still listed, and the secret is a new one.
  app = await launch()
  page = await app.firstWindow()
  await expect(page.getByRole('list', { name: 'Logs' }).getByRole('listitem')).toContainText(
    'car-circuit.vbo',
  )
  const coreAgain = await page.evaluate(() => window.trace.coreConnection())
  expect(coreAgain.secret).not.toBe(core.secret)
  await app.close()
})

test('a file that is not a .vbo is refused in plain words, and nothing is added', async () => {
  const notes = join(scratch, 'notes.txt')
  writeFileSync(notes, 'Tyre pressures for Saturday\n')

  const app = await launch()
  const page = await app.firstWindow()
  await expect(page.getByText('No Logs yet')).toBeVisible()

  await answerFileDialogWith(app, notes)
  await page.getByRole('button', { name: 'Import Log' }).click()

  const message = page.getByRole('alert')
  await expect(message).toContainText('notes.txt is not a Racelogic .vbo file')
  await expect(message).toContainText('Nothing was imported')
  await expect(page.getByText('No Logs yet')).toBeVisible()
  await app.close()
})
