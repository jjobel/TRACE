"""Generator of synthetic Racelogic `.vbo` fixtures with known lap times.

A Vehicle is driven round a flat oval Circuit by a simple model: full
acceleration out of each turn, a top speed, hard braking into the next turn.
Each Lap is given its lap time by scaling that speed profile, so the time
between two crossings of the Control line is known by construction and does
not depend on any lap-timing code.

The file layout follows Racelogic's published description of the format:
https://developers.racelogic.co.uk/Portal/Tutorials/tutorialVBOfilestructure.html

Run it to write a fixture by hand:

    python tests/synthetic_vbo.py car-circuit.vbo
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# The Circuit: two straights joined by two half-circle turns, driven
# anticlockwise. The Control line is across the middle of the main straight.
STRAIGHT = 900.0  # m
TURN_RADIUS = 120.0  # m
TURN = np.pi * TURN_RADIUS
LAP_DISTANCE = 2 * STRAIGHT + 2 * TURN
CONTROL_LINE_HALF_WIDTH = 15.0  # m

# Where the Circuit is: open water, so it cannot be mistaken for a real Venue.
VENUE = "TRACE Test Oval"
LATITUDE = 40.0  # degrees north
LONGITUDE = -30.0  # degrees east
HEIGHT = 12.0  # m
EARTH_RADIUS = 6_371_008.8  # m

# The car.
TURN_SPEED = 25.0  # m/s
TOP_SPEED = 60.0  # m/s
ACCELERATION = 4.0  # m/s²
BRAKING = 10.0  # m/s²
GEAR_TOP_SPEEDS = np.array([18.0, 28.0, 38.0, 48.0, 56.0, 66.0])  # m/s
ENGINE_SPEED_LIMIT = 7500.0  # rpm
FULL_BRAKE_PRESSURE = 80.0  # bar

# The Outing: it starts part-way round the Out-lap and ends part-way round
# the In-lap, both driven below the pace of a Lap.
OUT_LAP_DISTANCE = 1500.0  # m driven before the first crossing
IN_LAP_DISTANCE = 1100.0  # m driven after the last crossing
OUT_AND_IN_LAP_PACE = 0.8
PACE_CHANGE = (300.0, 600.0)  # m from the Control line between which the pace changes

LOG_RATE = 20  # Hz
DAY = "16/05/2026"  # the day the file says it was created on
GRID_STEP = 0.1  # m, the step the motion is integrated on

STANDARD_CHANNELS = (
    "satellites",
    "time",
    "latitude",
    "longitude",
    "velocity kmh",
    "heading",
    "height",
)
CAR_CHANNELS = {
    "Engine_Speed": "rpm",
    "Throttle_Position": "%",
    "Brake_Pressure": "bar",
    "Gear": "",
}
COLUMN_NAMES = ("sats", "time", "lat", "long", "velocity", "heading", "height", *CAR_CHANNELS)


@dataclass(frozen=True)
class SyntheticVbo:
    """A fixture file and what is known about it by construction."""

    path: Path
    lap_times: tuple[float, ...]  # s, one per Lap, in the order driven
    header: tuple[str, ...]  # the file's [header]: its columns, in order
    sample_count: int


def write_car_circuit_vbo(
    path: Path,
    lap_times: tuple[float, ...] = (68.512, 67.874, 68.139),
    first_sample_at: tuple[int, int, int] = (14, 2, 8),
) -> SyntheticVbo:
    """Write a car's Log of one Outing on the oval Circuit: Out-lap, Laps, In-lap.

    `first_sample_at` is the UTC time of day of the first sample, as hours,
    minutes and seconds.
    """
    motion = _drive(lap_times)
    x, y, heading = _place(motion.lap_position)

    latitude = LATITUDE + np.degrees(y / EARTH_RADIUS)
    longitude = LONGITUDE + np.degrees(x / (EARTH_RADIUS * np.cos(np.radians(LATITUDE))))
    gear = np.minimum(1 + np.searchsorted(GEAR_TOP_SPEEDS, motion.speed), len(GEAR_TOP_SPEEDS))
    engine_speed = ENGINE_SPEED_LIMIT * motion.speed / GEAR_TOP_SPEEDS[gear - 1]
    throttle = np.where(
        motion.acceleration < 0, 0.0, np.clip(20 + 80 * motion.acceleration / ACCELERATION, 0, 100)
    )
    brake_pressure = FULL_BRAKE_PRESSURE * np.clip(-motion.acceleration / BRAKING, 0, 1) + 0.0

    rows = [
        " ".join(
            [
                "009",
                _clock(first_sample_at, index),
                # Minutes of arc. The format counts longitude positive to the west.
                f"{latitude[index] * 60:012.5f}",
                f"{-longitude[index] * 60:012.5f}",
                f"{motion.speed[index] * 3.6:07.3f}",
                f"{heading[index]:06.2f}",
                f"{HEIGHT:+09.2f}",
                f"{engine_speed[index]:+.5E}",
                f"{throttle[index]:+.5E}",
                f"{brake_pressure[index]:+.5E}",
                f"{float(gear[index]):+.5E}",
            ]
        )
        for index in range(len(motion.speed))
    ]

    header = (*STANDARD_CHANNELS, *CAR_CHANNELS)
    hours, minutes, seconds = first_sample_at
    lines = [
        f"File created on {DAY} @ {hours:02d}:{minutes:02d}:{seconds:02d}",
        "",
        "[header]",
        *header,
        "",
        "[channel units]",
        *CAR_CHANNELS.values(),
        "",
        "[comments]",
        "Synthetic fixture written by the TRACE Telemetry fixture generator",
        f"Log Rate (Hz) : {LOG_RATE:.2f}",
        "",
        "[laptiming]",
        _control_line(),
        "",
        "[circuit details]",
        f"circuit {VENUE}",
        "",
        "[column names]",
        " ".join(COLUMN_NAMES),
        "",
        "[data]",
        *rows,
        "",
    ]
    path.write_bytes("\r\n".join(lines).encode("utf-8"))
    return SyntheticVbo(
        path=path,
        lap_times=tuple(lap_times),
        header=header,
        sample_count=len(rows),
    )


@dataclass(frozen=True)
class _Motion:
    """How the Vehicle is moving at each sample."""

    lap_position: np.ndarray  # m from the Control line, along the Circuit
    speed: np.ndarray  # m/s
    acceleration: np.ndarray  # m/s², along the path


def _drive(lap_times: tuple[float, ...]) -> _Motion:
    """Sample the Outing at the log rate, with each Lap taking its given time."""
    # One Lap on a fine grid of distance from the Control line. Driving it at
    # a pace of full_pace_lap_time / lap_time takes exactly lap_time.
    grid = np.arange(0.0, LAP_DISTANCE + GRID_STEP / 2, GRID_STEP)
    grid[-1] = LAP_DISTANCE
    full_pace_lap_time = _elapsed(grid, _profile_speed(grid))[-1]
    lap_paces = [full_pace_lap_time / lap_time for lap_time in lap_times]

    # Each part of the Outing is a stretch of the Circuit and the pace at each
    # point of it.
    # The Out-lap comes up to the pace of the first Lap, and the In-lap holds
    # the pace of the last Lap, well clear of the Control line, so the speed
    # does not step where a Lap is timed.
    near, far = PACE_CHANGE
    out_lap = _stretch(grid, LAP_DISTANCE - OUT_LAP_DISTANCE, LAP_DISTANCE)
    in_lap = _stretch(grid, 0.0, IN_LAP_DISTANCE)
    parts = [
        (
            out_lap,
            np.interp(
                out_lap,
                [LAP_DISTANCE - far, LAP_DISTANCE - near],
                [OUT_AND_IN_LAP_PACE, lap_paces[0]],
            ),
        )
    ]
    parts += [(grid, np.full(len(grid), pace)) for pace in lap_paces]
    parts += [(in_lap, np.interp(in_lap, [near, far], [lap_paces[-1], OUT_AND_IN_LAP_PACE]))]

    # Time, distance driven, speed and acceleration along the whole Outing.
    # Distance driven never falls back, unlike lap position.
    times, distances, speeds, accelerations = [], [], [], []
    elapsed = driven = 0.0
    for points, pace in parts:
        speed = pace * _profile_speed(points)
        part_time = _elapsed(points, speed)
        times.append(elapsed + part_time)
        distances.append(driven + points - points[0])
        speeds.append(speed)
        accelerations.append(speed * np.gradient(speed, points))  # a = v dv/ds
        elapsed += part_time[-1]
        driven += points[-1] - points[0]
    time = np.concatenate(times)
    sample_time = np.arange(int(elapsed * LOG_RATE) + 1) / LOG_RATE

    def at_samples(values: list[np.ndarray]) -> np.ndarray:
        return np.interp(sample_time, time, np.concatenate(values))

    return _Motion(
        lap_position=(out_lap[0] + at_samples(distances)) % LAP_DISTANCE,
        speed=at_samples(speeds),
        acceleration=at_samples(accelerations),
    )


def _stretch(grid: np.ndarray, start: float, end: float) -> np.ndarray:
    """The grid points from start to end, with both ends included exactly."""
    return np.concatenate([[start], grid[(grid > start) & (grid < end)], [end]])


def _profile_speed(lap_position: np.ndarray) -> np.ndarray:
    """Speed at full pace, by distance from the Control line along the Circuit."""
    half = STRAIGHT / 2
    # Distance along the current straight from the exit of the turn before it;
    # not used inside a turn.
    along_straight = np.select(
        [
            lap_position < half,
            (lap_position >= half + TURN) & (lap_position < half + TURN + STRAIGHT),
            lap_position >= half + 2 * TURN + STRAIGHT,
        ],
        [
            lap_position + half,
            lap_position - (half + TURN),
            lap_position - (half + 2 * TURN + STRAIGHT),
        ],
        default=0.0,
    )
    accelerating = np.sqrt(TURN_SPEED**2 + 2 * ACCELERATION * along_straight)
    braking = np.sqrt(TURN_SPEED**2 + 2 * BRAKING * (STRAIGHT - along_straight))
    return np.minimum(TOP_SPEED, np.minimum(accelerating, braking))


def _elapsed(distance: np.ndarray, speed: np.ndarray) -> np.ndarray:
    """Time taken to reach each distance: the integral of 1/speed."""
    slowness = 1.0 / speed
    steps = np.diff(distance) * (slowness[:-1] + slowness[1:]) / 2
    return np.concatenate([[0.0], np.cumsum(steps)])


def _place(lap_position: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """East and north of the Control line in metres, and the compass heading in degrees."""
    half = STRAIGHT / 2
    after_main = lap_position - half
    after_turn_1 = after_main - TURN
    after_back = after_turn_1 - STRAIGHT
    after_turn_2 = after_back - TURN
    angle_1 = after_main / TURN_RADIUS
    angle_2 = after_back / TURN_RADIUS
    segment = [after_main < 0, after_turn_1 < 0, after_back < 0, after_turn_2 < 0]

    x = np.select(
        segment,
        [
            lap_position,
            half + TURN_RADIUS * np.sin(angle_1),
            half - after_turn_1,
            -half - TURN_RADIUS * np.sin(angle_2),
        ],
        default=-half + after_turn_2,
    )
    y = np.select(
        segment,
        [
            0.0,
            TURN_RADIUS * (1 - np.cos(angle_1)),
            2 * TURN_RADIUS,
            TURN_RADIUS * (1 + np.cos(angle_2)),
        ],
        default=0.0,
    )
    # Driving east along the main straight, turning left.
    heading = np.select(
        segment,
        [90.0, 90.0 - np.degrees(angle_1), 270.0, 270.0 - np.degrees(angle_2)],
        default=90.0,
    )
    return x, y, heading % 360.0


def _clock(first_sample_at: tuple[int, int, int], sample: int) -> str:
    """UTC time of day of a sample, as hhmmss.ss. It starts again from zero at midnight."""
    hours, minutes, seconds = first_sample_at
    hundredths = (hours * 3600 + minutes * 60 + seconds) * 100 + sample * 100 // LOG_RATE
    hundredths %= 24 * 3600 * 100
    return (
        f"{hundredths // 360000:02d}"
        f"{hundredths // 6000 % 60:02d}"
        f"{hundredths % 6000 / 100:05.2f}"
    )


def _control_line() -> str:
    """The Start line of the Circuit as a `[laptiming]` entry: two end points,
    each as longitude then latitude, in minutes of arc."""
    points = []
    for north in (-CONTROL_LINE_HALF_WIDTH, CONTROL_LINE_HALF_WIDTH):
        points.append(f"{-LONGITUDE * 60:+012.6f}")
        points.append(f"{(LATITUDE + np.degrees(north / EARTH_RADIUS)) * 60:+012.6f}")
    return f"Start   {' '.join(points)} ¬ Start / Finish"


if __name__ == "__main__":
    target = Path(sys.argv[1]).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    written = write_car_circuit_vbo(target)
    print(f"{written.path}: {written.sample_count} samples, lap times {written.lap_times}")
