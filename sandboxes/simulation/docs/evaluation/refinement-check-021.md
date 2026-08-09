# Refinement check 021

The shared runtime now executes resident delivery collection after the delivery
is announced. The resident action is authorized by unit membership, the open
delivery projection becomes empty, and the delivery record remains in the
environment as collected history.

The refinement includes the collected delivery ID, status, and simulated
collection timestamp in the runtime projection.
