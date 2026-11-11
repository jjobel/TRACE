# ISO 8855 axis and sign convention for vehicle-frame channels

Vehicle-frame quantities (accelerations, rates, angles) need one sign convention, and the two standards disagree: ISO 8855:2011 uses x forward, y left, z up, while SAE J670 historically used z down, y right and since its 2008 revision allows either. We adopt ISO 8855 for every vehicle-frame Channel, because it is the international standard, MDF4 and most simulation tooling follow it, and it is the convention ISO 11838 (motorcycle kinematics) builds on for roll angle. Adapters for Sources that use SAE Z-down flip the affected signs.

## Consequences

- Positive lateral acceleration and positive yaw mean a turn to the left; positive pitch means nose down. Users coming from SAE-convention tools will see those signs reversed unless a view offers a display option.
- Three-wheelers and sidecars are covered by neither ISO 8855 nor ISO 11838; they use the ISO 8855 vehicle axes.
- Tyre slip angle sign and the ISO 11838 roll-angle details could not be verified from the paywalled texts; confirm them against the purchased standards before the Log format spec is finalized.
