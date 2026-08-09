# Refinement check 010

The MRL Runtime adapter now executes the maintenance queue observation in the
same shared environment as the status slice. It emits a manager attention
projection with count `3`, proving the queue behavior is available as replayable
runtime evidence rather than only as a pure helper result.

The runtime refinement keeps the January manager response separate from the
February queue action and adds semantic observations for resident intentions,
maintenance events, and manager status-change commands. The queue projection
is now traceable from actor pressure through domain behavior to manager-visible
output.
