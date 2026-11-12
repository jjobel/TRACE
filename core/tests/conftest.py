"""Shared fixtures: the core's local API called in-process, and fixture files."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from synthetic_vbo import SyntheticVbo, write_car_circuit_vbo

from trace_telemetry.api import create_app

SECRET = "the-secret-of-this-launch"


def open_api(data_dir: Path) -> TestClient:
    """The local API over a data folder, as a client that sends the secret."""
    app = create_app(data_dir=data_dir, secret=SECRET)
    return TestClient(app, headers={"Authorization": f"Bearer {SECRET}"})


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """The folder the core keeps its data in: empty at the start of each test."""
    return tmp_path / "application-data"


@pytest.fixture
def api(data_dir: Path) -> TestClient:
    return open_api(data_dir)


@pytest.fixture
def car_fixture(tmp_path: Path) -> SyntheticVbo:
    """A car's `.vbo` file somewhere outside the data folder, as a user would have it."""
    folder = tmp_path / "from-the-logger"
    folder.mkdir()
    return write_car_circuit_vbo(folder / "car-circuit.vbo")
