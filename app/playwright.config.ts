import { defineConfig } from '@playwright/test'

// End-to-end checks through the application's window. They launch the built
// application, so `npm test` builds it first.
export default defineConfig({
  testDir: 'e2e',
  timeout: 60_000,
  workers: 1,
  reporter: 'list',
})
