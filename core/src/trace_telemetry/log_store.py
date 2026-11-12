"""The Log store: imported Logs, kept in the user's application data folder.

Each Log has a folder of its own under `logs/`:

    logs/<log id>/
        log.json                      what the Log is; the catalog entry
        original/<file name>          the imported file, unchanged
        outing-1/channel-0001.parquet one file per Channel, in catalog order

A Channel's file has two columns, `time` (s from the Outing's time origin)
and `value`, at the Channel's own rate, and carries the Channel's name in its
metadata. Nothing is resampled. The catalog of Logs is the set of `log.json`
files.
"""

import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
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
        log_id = uuid.uuid4().hex
        # The Log is put together out of sight and moved into place in one
        # step, so a failed import leaves nothing half-imported.
        folder = self._incoming / log_id
        (folder / "original").mkdir(parents=True)
        try:
            # The Log is read from the kept copy, so the two always agree.
            original = Path(shutil.copy2(path, folder / "original" / path.name))
            log = read_vbo(original)
            for number, outing in enumerate(log.outings, start=1):
                outing_folder = folder / f"outing-{number}"
                outing_folder.mkdir()
                for index, channel in enumerate(outing.channels, start=1):
                    table = pa.table(
                        {"time": channel.times, "value": channel.values},
                        metadata={"channel": channel.name},
                    )
                    pq.write_table(table, outing_folder / f"channel-{index:04d}.parquet")
            stored = StoredLog(
                id=log_id,
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
            (folder / "log.json").write_text(stored.model_dump_json(indent=2), encoding="utf-8")
            self._logs.mkdir(parents=True, exist_ok=True)
            folder.rename(self._logs / log_id)
        except BaseException:
            shutil.rmtree(folder, ignore_errors=True)
            raise
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
