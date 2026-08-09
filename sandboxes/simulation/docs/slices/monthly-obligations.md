# Slice: monthly obligations

## Use-case contract

Across three simulated months, each unit receives one payment obligation. Two
units pay after the due date; one does not. The manager's overdue queue grows
from one to three outstanding obligations.

## Rules

- recurring obligations are generated once per month;
- overdue status is derived from simulated time;
- payment confirmation is a manual external handoff;
- a paid obligation cannot be paid again;
- no card data or provider integration is modeled.

## Done criteria

- deterministic monthly obligations are generated;
- late payment pressure is measurable over time;
- manual payment handoff updates status;
- repeated payment confirmation is rejected.

## Out of scope

Bank reconciliation, amount calculation, invoices, interest, collection,
payment providers, and accounting reports.
