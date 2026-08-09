# Refinement check 003

The shared-unit notification slice supports a provisional distinction:

- payment status is shared and remains visible without per-resident alerts;
- a maintenance status update is delivered once to each resident of the unit;
- repeated delivery on the same simulated day is idempotent;
- two requests in the same category/day aggregate into one notification without
  losing either request identity.

This is still a model hypothesis. Resident preferences, quiet hours, and
delivery channels require evidence from a later scenario or pilot.
