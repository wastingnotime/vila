# Slice: resident onboarding

## Use-case contract

A building manager invites a resident to a unit. The resident accepts the
invitation, activating current membership and status access.

## Rules

- invitations are manager-owned and uniquely identified;
- acceptance creates the first active membership period;
- invitation and acceptance are durable events;
- access does not exist before acceptance.

## Done criteria

- deterministic invitation acceptance works;
- current status follows the accepted unit;
- invitation lifecycle is replayable;
- rejected and expired invitations do not grant access.

## Out of scope

Email delivery, identity providers, ownership, leases, and administrator role
management.
