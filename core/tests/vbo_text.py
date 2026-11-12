"""Reads the text of a `.vbo` file for the tests.

It shares nothing with the Adapter or with the fixture generator, so what it
finds in a file is an independent check on both.
"""

from pathlib import Path

import numpy as np


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
    clock = column(path, "time")  # hhmmss.ss
    return (clock // 10000) * 3600 + (clock // 100 % 100) * 60 + clock % 100


def control_line_crossing_times(path: Path) -> np.ndarray:
    """When the path crosses the file's Start line, in seconds since midnight UTC.

    A crossing lies between the two samples either side of the line, and its
    time is interpolated linearly between them.
    """
    parts = sections(path)
    seconds = sample_times(path)
    # Both are in minutes of arc; the file's longitude is positive to the west.
    position = np.column_stack([column(path, "longitude"), column(path, "latitude")])
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


def column(path: Path, name: str) -> np.ndarray:
    """One column of the `[data]` section, by its name in the `[header]`."""
    parts = sections(path)
    index = parts["header"].index(name)
    return np.array([float(row.split()[index]) for row in parts["data"]])
