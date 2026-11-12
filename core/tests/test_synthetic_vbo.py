"""The fixture generator writes a car `.vbo` on a Circuit with known lap times.

The lap times are measured here from the text of the file alone: the Control
line in its `[laptiming]` section and the position samples in its `[data]`
section. Nothing is taken from how the generator builds the file.
"""

import numpy as np
import pytest
from synthetic_vbo import write_car_circuit_vbo
from vbo_text import control_line_crossing_times, sample_times, sections


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
