"""Where an imported Log is kept in the user's application data folder."""

from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from synthetic_vbo import write_car_circuit_vbo
from vbo_text import column


def stored_channels(log_folder: Path) -> dict[str, pa.Table]:
    """Every Channel file in a Log's folder, by the Channel name the file carries."""
    stored = {}
    for file in log_folder.rglob("*.parquet"):
        table = pq.read_table(file)
        stored[table.schema.metadata[b"channel"].decode()] = table
    return stored


def test_channel_data_is_stored_as_parquet_beside_the_unchanged_original(
    api, data_dir, car_fixture
):
    original = car_fixture.path.read_bytes()

    imported = api.post("/logs/import", json={"path": str(car_fixture.path)}).json()

    log_folder = data_dir / "logs" / imported["id"]
    stored = stored_channels(log_folder)
    assert len(stored) == len(car_fixture.header) - 1  # every column but time

    speed = stored["vbo.velocity kmh"]
    assert speed.column_names == ["time", "value"]
    assert speed["value"].to_pylist() == column(car_fixture.path, "velocity kmh").tolist()
    # Sample times count from the first sample, at the file's 20 Hz.
    assert speed["time"].to_pylist() == pytest.approx(
        (np.arange(car_fixture.sample_count) / 20).tolist(), abs=1e-6
    )

    assert (log_folder / "original" / "car-circuit.vbo").read_bytes() == original
    assert car_fixture.path.read_bytes() == original


def test_sample_times_keep_counting_when_an_outing_passes_midnight_utc(api, data_dir, tmp_path):
    # A .vbo file gives the UTC time of day, which starts again from zero at
    # midnight: early evening on the west coast of America, mid-morning in
    # eastern Australia.
    late = write_car_circuit_vbo(tmp_path / "late.vbo", first_sample_at=(23, 59, 50))

    imported = api.post("/logs/import", json={"path": str(late.path)}).json()

    speed = stored_channels(data_dir / "logs" / imported["id"])["vbo.velocity kmh"]
    assert speed["time"].to_pylist() == pytest.approx(
        (np.arange(late.sample_count) / 20).tolist(), abs=1e-6
    )
