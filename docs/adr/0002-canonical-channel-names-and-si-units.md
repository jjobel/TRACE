# Canonical channel names, SI units, position as a field

Views must work with any Source and any Vehicle, so they cannot depend on a Source's own channel names or units. The professional ecosystem gives no single standard to adopt: ASAM MDF4, MoTeC `.ld`, Racelogic `.vbo` and RaceCapture all store a free-text unit string per channel, none mandates SI, and no cross-vendor channel naming standard exists (MoTeC uses "Wheel Speed FL", AiM "GPS Speed", Bosch `vfzg` for comparable quantities). TRACE therefore defines its own canonical layer, aligned with industry practice where practice exists:

- **Units.** Every Channel is stored in SI units; the Adapter converts from the Source's unit string and records the original unit as provenance. Display units are a user preference whose defaults follow the trade (km/h, bar, °C, %, g), not SI.
- **Names.** Well-known quantities get a canonical, vehicle-neutral name (`speed`, `throttle`, `brake_pressure`). Each Adapter maps its Source's names to them through an alias table.
- **Position.** Position on the Vehicle is a separate structured field naming a Wheel position from the Vehicle's Layout or a whole axle (`brake_pressure` at `front`, never `brake_pressure_front`). Wheel position codes follow the industry's FL / FR / RL / RR convention, with F / R for single-track vehicles; no SAE or ISO wheel-code scheme was found.
- **Unmapped channels.** Channels with no canonical name are kept under a per-Source namespace (for example `motec.<name>`) so no data is lost.
- **Sampling.** Each Channel keeps its own sample times at its native rate, regular or irregular, on the Outing's time origin, as MDF4 does with one master per channel group. Nothing is resampled in storage; views resample when they draw.

## Consequences

- Adapters carry the burden of mapping and unit conversion; the core never converts.
- The canonical vocabulary becomes a contract that stored data depends on, so renaming a canonical channel later is a data migration, not a refactor.
- Exporting to MDF4 or MoTeC formats later is straightforward because their per-channel unit and rate model is a subset of TRACE's.
