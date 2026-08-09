# Slice: relevant activity history

## Use-case contract

The resident and manager can inspect a concise history related to the current
status. Residents see activity for their current unit; the manager sees
condominium activity. Entries use human-readable summaries rather than raw
event names or technical payloads.

## Rules

- activity is derived from the event history;
- activity history is not a second source of truth;
- resident visibility is limited to units in the resident's membership history;
- current status remains scoped only to the active unit;
- manager visibility is condominium-scoped;
- history supports understanding status but does not replace the prioritized
  status summary.

## Done criteria

- payment and maintenance events produce readable activity items;
- resident and manager visibility differ correctly;
- a moved resident can review their historical activity without gaining access
  to unrelated units;
- raw event names are not exposed as user-facing summaries;
- ordering is deterministic by simulated time.

## Out of scope

Full audit log, pagination, search, retention policy, resident-to-resident
visibility, and technical observability tooling.
