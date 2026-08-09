# Slice: manager-owned status inputs

## Use-case contract

Only a building manager can publish a condominium announcement or record a
delivery. Residents consume those items through status and history, but cannot
create them.

## Rules

- supplied actors are checked before state mutation;
- denied commands do not create announcements or deliveries;
- payment and maintenance role boundaries remain unchanged;
- internal deterministic fixtures may omit actor arguments when seeding state.

## Done criteria

- resident attempts are rejected;
- manager-owned state remains unchanged after rejection;
- runtime fixture uses an authorized manager actor for these commands.

## Out of scope

Concierge roles, administrator roles, delegation, announcement moderation, and
delivery hardware identity.
