# ADR 0001: Start with a small domain package

## Decision

The first implementation surface is a dependency-free Go package at
`packages/domain`. It owns condominium, unit membership, announcement,
payment obligation, maintenance request, and delivery behavior. The package
contains state transitions and invariant checks, but no HTTP, database, OIDC,
notification, or payment-provider code.

The application will use a modular-monolith shape when delivery surfaces are
added. API and persistence adapters must depend on this package rather than
reimplementing domain rules.

## Rationale

The seed asks the project to validate a low-cognitive-load workflow and to
cover core state transitions with tests. Starting with framework or storage
code would make the domain implicit and encourage screen-driven CRUD.

Maintenance status changes return an auditable transition record. Payment
cancellation requires an explicit restore before payment, and resolved or
rejected maintenance requests are terminal in this first version.

## Consequences

- IDs and persistence representations remain adapter concerns for now.
- Every aggregate includes its condominium ID where tenant scope applies.
- API payloads and database schemas are not yet public contracts.
- Transition rules can be refined as the pilot or simulation provides evidence.
