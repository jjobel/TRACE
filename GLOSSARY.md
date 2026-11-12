# TRACE

TRACE records, analyzes and coaches from motorsport telemetry produced by any vehicle and any data source. Its vocabulary follows FIA and FIM sporting usage and the terms the trade already uses; Sources are mapped onto these terms, never the other way round.

## Data

**Source**:
Anything that produces telemetry TRACE can ingest: a data logger, a GPS lap timer, a phone app, a sim, a public timing feed.
_Avoid_: Provider, input, game

**Adapter**:
The translator between one Source and TRACE's common format; the only place where source-specific knowledge lives.
_Avoid_: Plugin, driver, connector, importer

**Log**:
The data recorded from one vehicle in one go and brought into TRACE as a unit. It holds one or more Outings.
_Avoid_: Test, recording, file, session

**Channel**:
One named stream of measurements of one quantity, with a unit, its own sample times and an optional position on the vehicle.
_Avoid_: Signal, field, column, parameter

## Vehicle

**Vehicle**:
The machine the data was logged from, described by a display-only type (car, motorcycle, kart, sidecar…) and a Layout.
_Avoid_: Car (as the general term), bike (as the general term), machine

**Layout**:
The list of named wheel positions a Vehicle has, such as FL, FR, RL, RR for a car or F, R for a motorcycle.
_Avoid_: Configuration, wheel count

**Wheel position**:
One named wheel of a Vehicle's Layout; a Channel's position names a Wheel position or a whole axle (front, rear).
_Avoid_: Corner (as the general term), tyre position

## Time on track

**Event**:
A meeting at a Venue made up of one or more Sessions, such as a race weekend or a test day.
_Avoid_: Meeting, round, weekend

**Session**:
An officially scheduled period of track running within an Event, such as free practice, qualifying, a race or a warm-up.
_Avoid_: Outing, run, stint

**Outing**:
One continuous period on track by one Vehicle on one Course, from leaving the pit lane (or the start) to returning to it.
_Avoid_: Session, run, stint, test

**Out-lap**:
The part of an Outing from pit exit to the first crossing of the Control line. It is not a Lap.
_Avoid_: Warm-up lap

**In-lap**:
The part of an Outing from the last crossing of the Control line to pit entry. It is not a Lap.
_Avoid_: Pit-in lap, cool-down lap

## Course and timing

**Venue**:
The place one or more Courses are at, such as Silverstone.
_Avoid_: Track, circuit, location

**Course**:
The route a Vehicle is timed over, fixed by its Start line, its Finish line and its precise layout; changing any of the three makes a different Course.
_Avoid_: Track (when meaning the timed route), layout, configuration, stage

**Circuit**:
A Course whose Start line and Finish line are the same Control line.
_Avoid_: Loop, closed course

**Control line**:
A line at the crossing of which a Vehicle is timed. The Start line is a Course's first Control line and the Finish line its final one.
_Avoid_: Timing line, beacon, gate, start/finish (as the general term)

**Lap**:
One complete timed traversal of a Course: on a Circuit, between two consecutive crossings of the Control line on the track; on a point-to-point Course, from the Start line to the Finish line. A hill-climb heat is a Lap as much as a circuit lap is.
_Avoid_: Run, pass, attempt, heat (as the general term)

**Deleted lap**:
A complete Lap whose time does not count, for example for exceeding track limits. It is still a Lap, but is left out of best-lap comparisons by default.
_Avoid_: Invalid lap, cancelled lap, partial lap

**Sector**:
A part of a Course between two consecutive Control lines; every Lap on that Course is split into the same Sectors.
_Avoid_: Split, segment, intermediate (as the name of the part)
