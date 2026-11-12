"""The common Log format: what an Adapter turns a Source's file into."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Channel:
    """One named stream of measurements, with its own sample times."""

    name: str
    times: np.ndarray  # s, from the Outing's time origin
    values: np.ndarray


@dataclass(frozen=True)
class Outing:
    channels: tuple[Channel, ...]


@dataclass(frozen=True)
class Log:
    outings: tuple[Outing, ...]
