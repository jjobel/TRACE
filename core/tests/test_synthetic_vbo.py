"""The fixture generator writes a car `.vbo` on a Circuit with known lap times.

The lap times are measured here from the text of the file alone: the Control
line in its `[laptiming]` section and the position samples in its `[data]`
section. Nothing is taken from how the generator builds the file.
"""

from pathlib import Path

import numpy as np
import pytest
from synthetic_vbo import write_car_circuit_vbo


def test_car_fixture_holds_the_lap_times_it_was_asked_for(tmp_path):
    fixture = write_car_circuit_vbo(
        tmp_path / "car-circuit.vbo", lap_times=(68.512, 67.874, 68.139)
    )

    crossings = control_line_crossing_times(fixture.path)

    assert fixture.lap_times == (68.512, 67.874, 68.139)
    assert np.diff(crossings) == pytest.approx(fixture.lap_times, abs=0.005)


def test_car_fixture_has_an_out_lap_and_an_in_lap(tmp_path):
    fixture = write_car_circuit_vbo(tmp_path / "car-circuit.vbo")

    crossings = control_line_crossing_times(fixture.path)
    seconds = sample_times(fixture.path)

    assert crossings[0] - seconds[0] > 5.0
    assert seconds[-1] - crossings[-1] > 5.0


def test_car_fixture_reports_what_it_wrote(tmp_path):
    fixture = write_car_circuit_vbo(tmp_path / "car-circuit.vbo")

    parts = sections(fixture.path)

    assert fixture.channel_names == tuple(parts["header"])
    assert fixture.sample_count == len(parts["data"])
    assert {"velocity kmh", "Engine_Speed", "Throttle_Position", "Brake_Pressure"} <= set(
        fixture.channel_names
    )


def sections(path: Path) -> dict[str, list[str]]:
    """The non-blank lines of each `[section]` of a `.vbo` file."""
    found: dict[str, list[str]] = {}
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("[") and line.endswith("]"):
            current = found.setdefault(line[1:-1], [])
        elif current is not None and line.strip():
            current.append(line)
    return found


def sample_times(path: Path) -> np.ndarray:
    """Seconds since midnight UTC of every sample."""
    parts = sections(path)
    clock = _column(parts, "time")  # hhmmss.ss
    return (clock // 10000) * 3600 + (clock // 100 % 100) * 60 + clock % 100


def control_line_crossing_times(path: Path) -> np.ndarray:
    """When the path crosses the file's Start line, in seconds since midnight UTC.

    A crossing lies between the two samples either side of the line, and its
    time is interpolated linearly between them.
    """
    parts = sections(path)
    seconds = sample_times(path)
    # Both are in minutes of arc; the file's longitude is positive to the west.
    position = np.column_stack([_column(parts, "longitude"), _column(parts, "latitude")])
    line = [float(value) for value in parts["laptiming"][0].split()[1:5]]
    start, end = np.array(line[:2]), np.array(line[2:])
    along = end - start

    offset = position - start
    side = along[0] * offset[:, 1] - along[1] * offset[:, 0]
    crossings = []
    for i in np.nonzero(np.sign(side[:-1]) != np.sign(side[1:]))[0]:
        fraction = side[i] / (side[i] - side[i + 1])
        point = position[i] + fraction * (position[i + 1] - position[i])
        if 0.0 <= np.dot(point - start, along) / np.dot(along, along) <= 1.0:
            crossings.append(seconds[i] + fraction * (seconds[i + 1] - seconds[i]))
    return np.array(crossings)


def _column(parts: dict[str, list[str]], name: str) -> np.ndarray:
    index = parts["header"].index(name)
    return np.array([float(row.split()[index]) for row in parts["data"]])
