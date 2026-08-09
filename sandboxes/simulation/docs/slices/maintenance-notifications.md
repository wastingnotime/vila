# Slice: maintenance status notifications

## Use-case contract

When a manager changes a maintenance request for a shared unit to
`under_review`, every resident associated with that unit receives one concise
status-update notification. Repeating the same notification attempt on the
same simulated day is idempotent.

## Hypothesis under test

Payment obligations are unit-level status information and do not generate one
notification per resident. A maintenance status change is different: each
resident may need to understand what happened, so delivery is recipient-level.

## Done criteria

- shared-unit residents each receive one status-update notification;
- repeated delivery does not duplicate notifications;
- the status remains represented by the domain request and event history;
- no push provider or channel-specific implementation is introduced.

## Out of scope

Notification preferences, quiet hours, delivery notifications, mobile push,
email/SMS providers, and payment reminders.
