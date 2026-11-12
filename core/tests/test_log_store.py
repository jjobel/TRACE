"""Where an imported Log is kept in the user's application data folder."""

import numpy as np
import pyarrow.parquet as pq
import pytest
from vbo_text import column


def test_channel_data_is_stored_as_parquet_beside_the_unchanged_original(
    api, data_dir, car_fixture
):
    original = car_fixture.path.read_bytes()

    imported = api.post("/logs/import", json={"path": str(car_fixture.path)}).json()

    log_folder = data_dir / "logs" / imported["id"]
    stored = {}
    for file in log_folder.rglob("*.parquet"):
        table = pq.read_table(file)
        stored[table.schema.metadata[b"channel"].decode()] = table
    assert len(stored) == len(car_fixture.channel_names) - 1  # every column but time

    speed = stored["vbo.velocity kmh"]
    assert speed.column_names == ["time", "value"]
    assert speed["value"].to_pylist() == column(car_fixture.path, "velocity kmh").tolist()
    # Sample times count from the first sample, at the file's 20 Hz.
    assert speed["time"].to_pylist() == pytest.approx(
        (np.arange(car_fixture.sample_count) / 20).tolist(), abs=1e-6
    )

    assert (log_folder / "original" / "car-circuit.vbo").read_bytes() == original
    assert car_fixture.path.read_bytes() == original
