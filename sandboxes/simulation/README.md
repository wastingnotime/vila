# Condominium simulation

This is the pre-implementation model lab for Vila. It explores how a small
condominium behaves over simulated time before any production API or web
application is built.

The simulation is intentionally separate from production code. Its outputs are
observations, event streams, projections, and refined invariants—not a runtime
dependency for the future application.

Run the deterministic tests with:

```bash
python3 -m unittest discover -s sandboxes/simulation/tests -p 'test_*.py'
```

The WNT runtime adapter is available through:

```bash
mrl-simulation supervise --once
```

## First slice

The first slice models one resident and one building manager over a short
period. A late payment and a maintenance request should become visible as
prioritized status items, while routine events should not automatically create
notifications.
