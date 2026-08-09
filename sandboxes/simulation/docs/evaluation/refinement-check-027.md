# Refinement check 027

The shared runtime now emits an explicit empty status projection at scenario
start. It records no action items, no latest update, and no open deliveries
before later simulated activity begins.

The runtime invariants are now observation-window aware, so they do not report
false failures before the simulated state they validate has occurred.

The refinement verifies the empty projection correlation ID and confirms that
all emitted invariant results pass, including the initial observation window.
