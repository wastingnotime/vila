# Slice: role boundaries

## Use-case contract

A resident can submit a maintenance request. Only a building manager can
advance its status. Unknown actors cannot perform either role-scoped action.

## Rules

- roles are explicit in the simulation environment;
- resident commands require the resident role and an active membership;
- manager maintenance commands require the building-manager role;
- authorization failure does not append a domain event.

## Done criteria

- resident submission succeeds;
- resident status change is rejected;
- manager status change succeeds;
- unknown actors are rejected;
- denied commands leave event history unchanged.

## Out of scope

OIDC claims, invitations, role administration, administrator roles, and policy
editing.
