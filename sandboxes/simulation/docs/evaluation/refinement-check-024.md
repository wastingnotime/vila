# Refinement check 024

Payment confirmation is now represented in the simulation's event history and
activity projection. Replay restores the paid state, while user-facing history
uses `Payment marked paid` rather than a technical event name.

Repeated confirmation is rejected without appending a second payment event.
