"""The local API: how the user interface talks to the core.

It is internal to TRACE and versioned with the application.
"""

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from trace_telemetry.log_store import LogStore, StoredLog


class ImportRequest(BaseModel):
    path: Path


class LogSummary(BaseModel):
    id: str
    file_name: str
    imported_at: datetime


def create_app(data_dir: Path, secret: str) -> FastAPI:
    """The API over the Logs kept in one data folder."""
    store = LogStore(data_dir)
    app = FastAPI(title="TRACE Telemetry local API")

    @app.post("/logs/import", status_code=201)
    def import_log(request: ImportRequest) -> StoredLog:
        return store.import_file(request.path)

    @app.get("/logs")
    def list_logs() -> list[LogSummary]:
        return [LogSummary(**log.model_dump(exclude={"outings"})) for log in store.list_logs()]

    @app.get("/logs/{log_id}")
    def read_log(log_id: str) -> StoredLog:
        log = store.get_log(log_id)
        if log is None:
            raise HTTPException(status_code=404, detail="There is no Log with that id.")
        return log

    return app
