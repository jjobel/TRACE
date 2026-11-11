# Python analysis core, React UI, Electron desktop shell

TRACE must install and behave identically on Windows, macOS and Linux, work offline, and draw dense telemetry plots smoothly. We build it as three parts in one installed desktop application:

- **Analysis core in Python.** Adapters, Log storage, Lap and Sector detection, math channels and coaching analysis. Python has the strongest scientific stack (NumPy, Polars/pandas, SciPy) and is the language motorsport engineers most often already script in, which widens the contributor pool.
- **User interface in React and TypeScript.** Talks to the core over a local API bound to the loopback interface. The core decimates Channel data to what the view can show before sending it, because browser plotting libraries slow down beyond roughly 100k points in view.
- **Electron as the desktop shell.** Ships its own Chromium, so rendering, and in particular GPU-drawn plots, is identical on every OS. Electron starts the Python core as a bundled sidecar process.

## Considered options

- **PySide6 + pyqtgraph (native Qt).** Fastest native plotting and a single language, but a separate web build would be needed for any second-screen or tablet view, and the Qt UI contributor pool is smaller than the web one.
- **Tauri 2 + Python sidecar.** Much smaller download and lower memory use, but it renders with each OS's own web engine; WebKitGTK on Linux has known WebGL slow paths, which conflicts with identical behaviour on every OS.
- **Tauri + Rust core.** Fastest overall, but replaces Python's analysis ecosystem and narrows contributors to Rust developers.
- **Python + pywebview.** Simplest packaging, but shares Tauri's system-webview rendering differences.

## Consequences

- Downloads are larger (about 150 MB for the shell, plus the bundled Python runtime) and memory use is higher than Tauri or Qt; accepted for a desktop analysis tool.
- Two languages and a local API contract between them. The API is TRACE-internal and versioned with the app.
- The local API makes a later second-screen or pit-wall view on the local network possible; it stays loopback-only until that is designed deliberately.
- The Electron shell must follow Electron's security guidance (context isolation, no Node integration in the renderer, sandboxed renderer).
