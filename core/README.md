# TRACE Telemetry analysis core

The Python part of TRACE: Adapters, Log storage and the local API the user interface talks to. See [ADR 0005](../docs/adr/0005-python-core-react-ui-electron-shell.md).

It is started by the desktop shell and is not meant to be run on its own. To work on it you need [uv](https://docs.astral.sh/uv/); the tests are run with `uv run pytest` from this folder, or with `npm test` from the repository root together with all the others.
