import { resolve } from 'node:path'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'electron-vite'

// The application in TRACE's own words: the shell is Electron's main process
// with its preload script, the ui is what the window shows.
export default defineConfig({
  main: {
    build: { outDir: 'out/shell', lib: { entry: 'src/shell/main.ts' } },
  },
  preload: {
    build: { outDir: 'out/preload', lib: { entry: 'src/shell/preload.ts' } },
  },
  renderer: {
    root: 'src/ui',
    build: { outDir: 'out/ui', rolldownOptions: { input: resolve('src/ui/index.html') } },
    plugins: [react()],
  },
})
