# Refinement check 076

The runtime adapter now exposes an observatory graph for the shared simulation:
resident and manager actors feed domain flows, which feed status, notification,
and activity projections.

Actors and cross-domain projections remain shared in filtered views, while
domain flows use renderer-supported layers so structural beams retain visible
endpoints and depth.

Notifications use a separate event lane from projections to avoid visual
overlap in the all-domains graph.
