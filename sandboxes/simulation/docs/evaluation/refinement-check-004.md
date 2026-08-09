# Refinement check 004

The movement slice confirms that resident status is current-membership scoped:
moving from unit 101 to unit 102 leaves previous-unit maintenance history
intact but does not expose it as current status. Membership boundaries use a
half-open interval: the old membership ends exactly when the new one begins.

Departure now closes the active membership and removes current resident access
without deleting the historical membership record.

Ownership, lease semantics, and transfer approval remain outside the simulation
until a scenario requires them.
