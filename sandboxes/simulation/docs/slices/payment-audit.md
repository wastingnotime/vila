# Slice: payment audit activity

## Use-case contract

When a manager confirms a payment handoff, the payment transition is appended
to domain history, can be replayed, and appears as human-readable activity for
the addressed resident and manager.

## Rules

- payment processing remains external;
- local confirmation is an auditable domain event;
- historical replay reconstructs paid state;
- activity uses plain language rather than raw event names.

## Done criteria

- payment confirmation appends an event;
- replay restores paid status and timestamp;
- resident activity includes the paid transition;
- no card data or provider payload is stored.

## Out of scope

Receipts, settlement, reconciliation, interest, refunds, chargebacks, and
provider webhooks.
