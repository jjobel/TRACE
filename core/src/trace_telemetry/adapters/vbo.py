"""Reads Racelogic `.vbo` files.

The format is described by Racelogic at
https://developers.racelogic.co.uk/Portal/Tutorials/tutorialVBOfilestructure.html

This is the first, thin version: every column is kept as it was recorded,
under the `vbo.` namespace.
"""

from pathlib import Path

import numpy as np

from trace_telemetry.adapters import UnreadableFile
from trace_telemetry.log import Channel, Log, Outing

NAMESPACE = "vbo"


def read_vbo(path: Path) -> Log:
    """Turn a `.vbo` file into a Log of one Outing."""
    sections = _sections(path.read_text(encoding="utf-8", errors="replace"))
    if "header" not in sections or "data" not in sections:
        raise UnreadableFile(
            f"{path.name} is not a Racelogic .vbo file: "
            "it has no [header] section or no [data] section."
        )
    header = sections["header"]
    data = np.array([[float(value) for value in row.split()] for row in sections["data"]])

    # The time column is the UTC time of day as hhmmss.ss. It gives every
    # Channel its sample times, counted from the first sample.
    clock = data[:, header.index("time")]
    seconds = (clock // 10000) * 3600 + (clock // 100 % 100) * 60 + clock % 100
    times = seconds - seconds[0]

    channels = tuple(
        Channel(name=f"{NAMESPACE}.{name}", times=times, values=data[:, column])
        for column, name in enumerate(header)
        if name != "time"
    )
    return Log(outings=(Outing(channels=channels),))


def _sections(text: str) -> dict[str, list[str]]:
    """The non-blank lines under each `[section]` heading."""
    sections: dict[str, list[str]] = {}
    lines = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            lines = sections.setdefault(line[1:-1], [])
        elif line and lines is not None:
            lines.append(line)
    return sections
