# Slice: notification fatigue

## Selected implementation pack

Python event-sourced simulation with deterministic time. This slice extends
the shared condominium environment and does not create a second simulation.

## Use-case contract

When three units become overdue and one maintenance request is submitted, the
manager sees all four actionable items in status. The manager receives one
maintenance review notification, not one notification per overdue payment.
Refreshing status on the same simulated day does not duplicate the notification.

## Hypothesis under test

Overdue obligations are important status information but are not individually
notification-worthy. Maintenance requests that need review are actionable and
can be grouped into one daily notification by category and recipient.

## Deterministic scenario

Start on 2026-01-01 UTC with three units and one resident per unit. On
2026-01-06, all three payments are overdue and resident 1 submits a plumbing
request. Inspect manager status and notification output twice.

## Done criteria

- three overdue obligations remain visible in manager status;
- exactly one maintenance review notification is emitted;
- the notification includes the number of reviewable requests;
- a repeated status refresh is idempotent;
- no payment-provider or delivery behavior is introduced.

## Out of scope

Push providers, notification preferences, escalation, quiet hours, delivery
notifications, and resident-specific notification channels.
