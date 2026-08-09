# Refinement check 016

The runtime refinement makes projections simulated-time aware. Requests,
deliveries, and activity entries created after a queried instant are excluded.
The runtime now records an invariant proving that resident and manager summary
scope remains correct at the summary instant even after later queue actions.
