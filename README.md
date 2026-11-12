# TRACE
TRACE: Telemetry Recording, Analysis &amp; Coaching Engine. Open-source telemetry analysis for sim racing and motorsport data.

## Running from source

TRACE is at an early stage. Today it opens a window, imports a Racelogic `.vbo` file and lists the Log in the library.

You need [Node.js](https://nodejs.org/) 22.12 or newer and [uv](https://docs.astral.sh/uv/), which looks after Python and the core's packages. Everything else is installed inside this folder.

```bash
npm install
```

```bash
npm start
```

```bash
npm test
```

- `npm install` fetches the desktop application's packages. The first `npm start` also downloads Electron, once.
- `npm start` builds TRACE and runs it. `npm run dev` runs it with the user interface reloading as you edit.
- `npm test` runs every test: the core's, then a check through the application's window.

To try an import without a logger file of your own, write the synthetic one the tests use:

```bash
uv run --project core python core/tests/synthetic_vbo.py ~/Desktop/car-circuit.vbo
```

Imported Logs are kept in your application data folder, on macOS `~/Library/Application Support/TRACE Telemetry/library`. The file you import from is never changed.

| Folder | Holds |
|---|---|
| `core/` | The analysis core, in Python: Adapters, the Log store and the local API |
| `app/` | The desktop application: the Electron shell (`src/shell`) and the user interface (`src/ui`) |
| `docs/` | Decision records and the design system |

## License

Copyright (C) 2026 Jose E. Jobel and TRACE contributors.

TRACE is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. See [LICENSE](LICENSE).
