# Refinement check 032

Membership moves, departures, and re-entry now have durable domain events.
Replaying the environment history reconstructs the resident's membership
periods and current unit instead of relying on the mutated live environment.
