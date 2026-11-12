"""The Log store: imported Logs, kept in the user's application data folder.

Each Log has a folder of its own under `logs/`, holding `log.json`, which
describes it. The catalog of Logs is the set of those descriptions.
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from trace_telemetry.adapters.vbo import read_vbo


class StoredChannel(BaseModel):
    name: str
    samples: int


class StoredOuting(BaseModel):
    channels: list[StoredChannel]


class StoredLog(BaseModel):
    id: str
    file_name: str
    imported_at: datetime
    outings: list[StoredOuting]


class LogStore:
    def __init__(self, data_dir: Path) -> None:
        self._logs = data_dir / "logs"
        self._incoming = data_dir / "incoming"

    def import_file(self, path: Path) -> StoredLog:
        """Read a file with its Adapter and add the Log to the store."""
        log = read_vbo(path)
        stored = StoredLog(
            id=uuid.uuid4().hex,
            file_name=path.name,
            imported_at=datetime.now(UTC),
            outings=[
                StoredOuting(
                    channels=[
                        StoredChannel(name=channel.name, samples=len(channel.values))
                        for channel in outing.channels
                    ]
                )
                for outing in log.outings
            ],
        )

        # The Log is put together out of sight and moved into place in one
        # step, so a failed import leaves nothing half-imported.
        folder = self._incoming / stored.id
        folder.mkdir(parents=True)
        (folder / "log.json").write_text(stored.model_dump_json(indent=2), encoding="utf-8")
        self._logs.mkdir(parents=True, exist_ok=True)
        folder.rename(self._logs / stored.id)
        return stored

    def list_logs(self) -> list[StoredLog]:
        """Every Log in the store, in the order they were imported."""
        logs = [
            StoredLog.model_validate_json(description.read_text(encoding="utf-8"))
            for description in self._logs.glob("*/log.json")
        ]
        return sorted(logs, key=lambda log: (log.imported_at, log.id))

    def get_log(self, log_id: str) -> StoredLog | None:
        return next((log for log in self.list_logs() if log.id == log_id), None)
