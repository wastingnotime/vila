# Refinement check 023

Manager-owned announcement publication and delivery recording now have explicit
actor checks. Resident attempts are rejected before state mutation, while the
runtime fixture supplies the manager actor for both commands.

The refinement makes the manager actor mandatory for these command methods,
removing the fixture-only authorization bypass while preserving explicit
manager actors in deterministic scenarios.
