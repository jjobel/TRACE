"""Runs the core as the desktop shell's sidecar process.

    TRACE_API_SECRET=<secret> python -m trace_telemetry --data-dir <folder>

The core listens on a free port of the loopback interface and says which on
its standard output, as one line of JSON: `{"port": 51234}`. It serves the
local API there to callers that have the secret.

It stops when its standard input closes. The shell holds that open for as
long as it runs, so the core never outlives the shell, however the shell ends.
"""

import argparse
import json
import os
import socket
import sys
import threading
from pathlib import Path

import uvicorn

from trace_telemetry.api import create_app

LOOPBACK = "127.0.0.1"
SECRET_VARIABLE = "TRACE_API_SECRET"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="trace_telemetry", description="The TRACE Telemetry analysis core."
    )
    parser.add_argument(
        "--data-dir", type=Path, required=True, help="the folder Logs are kept in"
    )
    parser.add_argument(
        "--ui-origin", help="the web origin the user interface is served from"
    )
    arguments = parser.parse_args()
    # The secret comes in the environment, not as an argument, because the
    # arguments of a process can be read by every user of the machine.
    secret = os.environ.get(SECRET_VARIABLE)
    if not secret:
        parser.error(f"the secret of this launch must be given in {SECRET_VARIABLE}")

    app = create_app(
        data_dir=arguments.data_dir, secret=secret, ui_origin=arguments.ui_origin
    )
    server = uvicorn.Server(
        uvicorn.Config(app, log_level="warning", timeout_graceful_shutdown=5)
    )

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((LOOPBACK, 0))  # port 0: the system picks a free one
    listener.listen()
    threading.Thread(target=_stop_when_input_closes, args=(server,), daemon=True).start()
    print(json.dumps({"port": listener.getsockname()[1]}), flush=True)
    server.run(sockets=[listener])


def _stop_when_input_closes(server: uvicorn.Server) -> None:
    if sys.stdin is None:  # started with no input at all: nothing to watch
        return
    while sys.stdin.buffer.read(4096):
        pass
    server.should_exit = True


if __name__ == "__main__":
    main()
