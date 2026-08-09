# Slice: status and obligations

## Selected implementation pack

Python event-sourced simulation with deterministic simulated time and the WNT
MRL Runtime adapter.

## Use-case contract

Given a resident associated with a unit, advance simulated time past a payment
due date, and open a maintenance request. The resident status summary exposes
the overdue payment and open request in priority order. A manager can advance
the request and sees the same request in the manager queue.

## Rules

- payment processing remains external;
- overdue is derived from simulated time and obligation due date;
- maintenance transitions are explicit and recorded as events;
- a status summary is a projection, not a second source of truth;
- no notification is emitted merely because a payment becomes overdue.

## Deterministic scenario

Start on 2026-01-01 UTC with unit 101, resident `resident-1`, manager
`manager-1`, and a payment due on 2026-01-05. On 2026-01-06, open a plumbing
request and inspect both status summaries.

## Done criteria

- event history can reconstruct the scenario state;
- overdue payment and submitted request appear in the resident summary;
- manager queue contains the submitted request;
- every request transition records who changed it and when;
- invariant checks pass deterministically;
- runtime adapter returns a valid `Scenario`.

## Out of scope

Announcements, deliveries, OIDC, payment provider behavior, persistence,
browser interaction, and production API contracts.
