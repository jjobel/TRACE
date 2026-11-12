"""The local API: how the user interface talks to the core.

It is internal to TRACE and versioned with the application.
"""

import logging
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from trace_telemetry.adapters import UnreadableFile
from trace_telemetry.log_store import LogStore, LogSummary, StoredLog

logger = logging.getLogger(__name__)


class ImportRequest(BaseModel):
    path: Path


class _RequireSecret:
    """Turns away every request that does not carry the secret of this launch.

    The desktop shell makes the secret up at each launch and gives it only to
    the core and to the user interface, so other programs and web pages on
    the machine cannot call the API.
    """

    def __init__(self, app: ASGIApp, secret: str) -> None:
        self._app = app
        self._expected = f"Bearer {secret}".encode()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            given = Headers(scope=scope).get("authorization", "").encode()
            if not secrets.compare_digest(given, self._expected):
                refusal = JSONResponse(
                    {"detail": "This request does not carry the secret of this launch."},
                    status_code=401,
                )
                await refusal(scope, receive, send)
                return
        await self._app(scope, receive, send)


def create_app(data_dir: Path, secret: str, ui_origin: str | None = None) -> FastAPI:
    """The API over the Logs kept in one data folder, for callers that have the secret.

    `ui_origin` is the web origin the user interface is served from. A browser
    lets pages from that origin, and no other, send requests to the API.
    """
    store = LogStore(data_dir)
    app = FastAPI(title="TRACE Telemetry local API")
    app.add_middleware(_RequireSecret, secret=secret)
    if ui_origin is not None:
        # Added last, so it is outermost: a browser's preflight request carries
        # no secret and has to be answered before the secret is asked for.
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[ui_origin],
            allow_methods=["*"],
            allow_headers=["Authorization", "Content-Type"],
        )

    @app.post("/logs/import", status_code=201)
    def import_log(request: ImportRequest) -> StoredLog:
        name = request.path.name
        try:
            return store.import_file(request.path)
        except UnreadableFile as unreadable:
            raise HTTPException(
                status_code=400,
                detail=f"{unreadable.cause} Nothing was imported. {unreadable.remedy}",
            ) from unreadable
        except Exception as fault:
            # Answered here, not left to the server, so that the user interface
            # is told in words it can show.
            logger.exception("Importing %s failed", request.path)
            raise HTTPException(
                status_code=500,
                detail=(
                    f"TRACE could not read {name}; the file may be damaged. "
                    "Nothing was imported. If the logger's own software opens the file, "
                    "please report this as a fault in TRACE."
                ),
            ) from fault

    @app.get("/logs", response_model=list[LogSummary])
    def list_logs() -> list[StoredLog]:
        return store.list_logs()

    @app.get("/logs/{log_id}")
    def read_log(log_id: str) -> StoredLog:
        log = store.get_log(log_id)
        if log is None:
            raise HTTPException(status_code=404, detail="There is no Log with that id.")
        return log

    return app
