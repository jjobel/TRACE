import { execFileSync } from 'node:child_process'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

import { _electron as electron, expect, test, type ElectronApplication } from '@playwright/test'

const appFolder = resolve(__dirname, '..')
const coreFolder = resolve(appFolder, '..', 'core')

let scratch: string

test.beforeEach(() => {
  scratch = mkdtempSync(join(tmpdir(), 'trace-e2e-'))
})

test.afterEach(() => {
  rmSync(scratch, { recursive: true, force: true })
})

/** Starts the application from source, keeping its data in a folder of the test's own. */
function launch(): Promise<ElectronApplication> {
  return electron.launch({
    args: [appFolder],
    env: { ...process.env, TRACE_USER_DATA_DIR: join(scratch, 'user-data') },
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

test('a .vbo imported through the file dialog is in the library, and still there after a restart', async () => {
  const fixture = writeCarFixture()

  // Starting the application opens a window and starts the core: the library
  // can only say it is empty once the core has answered.
  let app = await launch()
  let page = await app.firstWindow()
  await expect(page.getByRole('heading', { name: 'Library' })).toBeVisible()
  await expect(page.getByText('No Logs yet')).toBeVisible()

  // The file dialog is the operating system's own, so the test answers for
  // the user: it "chooses" the fixture, and notes what the dialog was asked.
  await app.evaluate(({ dialog }, chosen) => {
    dialog.showOpenDialog = (async (...asked: unknown[]) => {
      ;(globalThis as Record<string, unknown>).askedOfDialog = asked.at(-1)
      return { canceled: false, filePaths: [chosen] }
    }) as typeof dialog.showOpenDialog
  }, fixture)
  await page.getByRole('button', { name: 'Import Log' }).click()

  const logs = page.getByRole('list', { name: 'Logs' })
  await expect(logs.getByRole('listitem')).toHaveCount(1)
  await expect(logs.getByRole('listitem')).toContainText('car-circuit.vbo')
  const asked = await app.evaluate(() => (globalThis as Record<string, unknown>).askedOfDialog)
  expect(asked).toMatchObject({ filters: [{ extensions: ['vbo'] }] })

  // The core's API is on the loopback interface and wants the secret.
  const core = await page.evaluate(() => window.trace.coreConnection())
  expect(new URL(core.baseUrl).hostname).toBe('127.0.0.1')
  expect((await fetch(`${core.baseUrl}/logs`)).status).toBe(401)

  // Quitting the application stops the core.
  await app.close()
  await expect(async () => {
    await expect(fetch(`${core.baseUrl}/logs`)).rejects.toThrow()
  }).toPass({ timeout: 10_000 })

  // After a restart the Log is still listed.
  app = await launch()
  page = await app.firstWindow()
  await expect(page.getByRole('list', { name: 'Logs' }).getByRole('listitem')).toContainText(
    'car-circuit.vbo',
  )
  await app.close()
})
