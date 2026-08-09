# Slice: important announcements

## Use-case contract

Residents can see a concise latest-update list. Active high-priority
announcements appear before normal updates. Expired announcements disappear
from the active view but remain in the simulation history.

## Rules

- announcements are condominium-wide within their own condominium;
- announcements from another condominium are never visible;
- publication starts at an inclusive timestamp;
- expiration ends at an exclusive timestamp;
- high-priority updates are ordered before normal updates;
- an announcement is information, not automatically an action item.

## Done criteria

- active announcements are time-scoped;
- priority ordering is deterministic;
- equal-priority ties are deterministic;
- expiration does not delete history;
- announcement visibility does not change payment or maintenance status counts.

## Out of scope

Acknowledge/read tracking, targeted announcements, drafts, rich media, legal
notice workflows, and push delivery.
