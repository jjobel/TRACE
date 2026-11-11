# Project brief: TRACE

**TRACE: Telemetry Recording, Analysis & Coaching Engine.** Open-source telemetry analysis software for any motorsport vehicle.

Items marked **Decided** were confirmed by Elias. Items marked **Proposed** were discussed but not confirmed; challenge them before building on them.

## What this is

Desktop software that takes telemetry from any motorsport vehicle and turns it into the kind of analysis race engineers do in tools like MoTeC i2: lap overlays, time deltas, track maps, and eventually automatic insights. If a user has data, they can analyze it.

## Core principle: nothing is hardcoded to one use case (Decided)

This is the most important requirement in this brief. TRACE is not "ACC software" or "car software".

- **Any vehicle.** Cars, motorcycles, dirt bikes, karts, three-wheelers, and anything else that produces data. No code may assume four wheels, a steering wheel, or a specific channel list.
- **Any source.** Sims, real-world data loggers, GPS lap timers, phone apps, public race data. Each source is an adapter; the core never knows which one produced the data.
- **Works with whatever the data contains.** A GPS-only file still gets a track map, speed trace, and lap comparison. Richer data unlocks more views.

Design rules that follow:

1. **Channels are a flexible list, not a fixed schema.** Each channel carries a name, unit, sample rate, and optional position on the vehicle (for example front or rear brake, a specific wheel).
2. **Each session declares its vehicle type and layout** (wheel count, and so on) as metadata. Views adapt to it.
3. **Views declare which channels they need** and appear only when the data has them.
4. **Laps and track position are the universal layer.** Overlays, deltas, sectors, and corner detection work for any vehicle on a circuit.
5. **Adapters are the only source-specific code.** Adding a source or vehicle must never require changing the core.
6. **Tests prove it.** The core is tested with at least one non-car fixture (for example a synthetic motorcycle session) from phase 1, so car assumptions fail in CI.

Scope boundary (Proposed): motorsport vehicle data on a track or course. Not a general-purpose data analysis tool. Point-to-point disciplines (rally stages, hill climbs, motocross variations) need thought about what "lap" means.

## Other non-negotiables (Decided)

- **Real engineering, not vibe coding.** Specs before code, tests first, code review on every change, documented decisions. The project should be something other engineers respect.
- **Open source, at the caliber of GIMP or Inkscape.** Public repo, proper releases, real installers, contributor documentation. License not yet chosen.
- **Ships as an installer.** End users download and install it like any desktop application. Cloning the repo is for contributors only.
- **Phase 1 first, with ACC as the first data source.** Assetto Corsa Competizione is the first adapter because Elias can test against it. It is the first adapter, not the product.

## Phase 1 scope (Decided in outline, details to be specified)

1. **Common session format** and the adapter interface, vehicle-neutral per the rules above.
2. **ACC adapter (recorder):** read ACC's shared memory while the user drives and save each session.
3. **Lap segmentation:** split a session into laps with lap and sector times.
4. **Replay tool:** play a recorded session back through the same pipeline, so everything downstream can be developed and tested without the sim.

Proposed addition: a "walking skeleton" release in phase 1, where CI builds a real installer from the first milestone.

## Later phases (Proposed, not committed)

2. Analysis UI: lap overlays by distance, time-delta trace, track map, corner detection.
3. File-import adapter (CSV and common logger formats). This is what opens TRACE to real bikes, karts, and cars.
4. Live dashboard (pit-wall view on a second screen).
5. Engineering views: tyres, brakes, suspension, fuel, lean angle, math channels, each shown when the data supports it.
6. Insights: per-corner reports, theoretical best lap, coaching.
7. More adapters: other sims, ACC broadcasting API, MoTeC .ld import, FastF1 (F1), PyMotoGP (MotoGP timing).

## Data sources researched so far

- **ACC shared memory (phase 1):** rich live data for the player's car. Windows only.
- **FastF1:** real F1 timing and telemetry. Since 15 Oct 2026 it needs each user's own F1 TV login. The repo must never ship F1 data.
- **PyMotoGP:** MotoGP lap times, sectors, and top speeds. Timing only; no public source for MotoGP telemetry traces was found.
- **Rider and driver loggers:** not yet researched. Which file formats matter most is an open question.

## Architecture (Proposed)

- Python core and backend (FastAPI, WebSockets for live data).
- Local storage in DuckDB/Parquet. Local-first; no cloud dependency.
- React + TypeScript frontend.
- Cross-platform app (Windows, macOS, Linux), since a rider importing a file may be on any OS. Only the ACC live adapter is Windows-only.
- Packaging: PyInstaller bundle with the UI in a native window; Inno Setup installer on Windows, DMG on macOS, AppImage on Linux. A Tauri shell is the alternative.

## Release and distribution (Proposed, modeled on GIMP and Inkscape)

- CI builds every installer from source on every tagged release; nothing is built by hand.
- Versioned releases with release notes, published on GitHub Releases.
- Development (nightly) builds from the main branch for testers.
- A small project website with a download page and user documentation.
- Standard community files: `README`, `LICENSE`, `CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`, issue and pull-request templates.
- A documented guide for writing a new adapter, since adapters are the main contribution path.

## Known constraints and risks

- The ACC adapter only runs on Windows next to the sim. Elias's linked dev machine is a Mac, so the record/replay split is what makes Mac development possible. A real recorded session is needed early as a test fixture.
- Generality is the main design risk: the easy path is to hardcode ACC's channels in phase 1 and pay for it later. The design rules above exist to prevent that.
- Unsigned installers trigger warnings on Windows and macOS. Signing options and cost need research.
- Do not promise F1-team depth; most sources do not expose aero or tyre-model data.

## Open questions

- Where does ACC run (which Windows PC), and how does a recorded session get to the dev machine?
- Confirm or replace the Python + React stack and the packaging approach.
- The session format: storage, units, channel naming conventions, vehicle metadata.
- How non-circuit disciplines fit the "lap" model.
- Repo name (plain `trace` is a common word), license, and supported OS versions. TRACE has not been checked for name conflicts.
- What "done" means for phase 1 (acceptance tests).
