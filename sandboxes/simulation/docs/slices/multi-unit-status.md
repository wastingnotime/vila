# Slice: multi-unit status summary

## Use-case contract

In a three-unit condominium, a resident sees only their unit's overdue payment
and maintenance request. The manager sees overdue obligations, maintenance
attention, and open deliveries across all units.

## Rules

- resident summaries are current-unit scoped;
- manager summaries are condominium-scoped;
- the same projection shape serves both roles;
- visibility differences come from domain authorization and membership, not
  separate dashboard logic.

## Done criteria

- resident cannot see another unit's delivery;
- manager sees all overdue obligations;
- manager sees cross-unit open deliveries;
- action ordering remains deterministic.

## Out of scope

Per-unit manager delegation, owner associations, dashboards, charts, and
customized manager filters.
