# Slice: membership history

## Use-case contract

When a resident moves from unit 101 to unit 102, their current status follows
unit 102. A maintenance request opened while they occupied unit 101 remains
associated with unit 101 and remains auditable.

## Rules

- membership periods are time-bounded and retained;
- a resident has at most one active unit at a simulated instant;
- current status uses the active membership, not historical membership;
- historical requests are not reassigned when a resident moves;
- a resident without an active membership cannot resolve a current unit.

## Done criteria

- movement creates a closed old membership and an open new membership;
- status after movement does not leak old-unit items;
- old-unit activity remains queryable;
- deterministic tests cover the boundary instant.

## Out of scope

Ownership, leases, rent, transfer approvals, manager reassignment, and legal
retention policy.
