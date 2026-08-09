# Slice: composed status summary

## Use-case contract

The primary status view combines actionable items, the latest important
announcement, and open deliveries. Action items appear first; informational
updates remain separate from the action list.

## Rules

- resident actions are current-unit scoped;
- manager actions are condominium-scoped;
- overdue payments, maintenance work, and deliveries are actionable items;
- the latest announcement is informational unless another rule explicitly
  promotes it to an action;
- the projection composes existing domain behavior and stores no new state.

## Done criteria

- resident and manager summaries differ by visibility scope;
- action ordering is deterministic;
- latest announcement does not inflate action counts;
- open deliveries are represented without exposing unrelated units.
- an empty summary explicitly represents no current action, update, or delivery.

## Out of scope

Dashboard charts, personalization, widgets, recommendation ranking, and
channel-specific rendering.
