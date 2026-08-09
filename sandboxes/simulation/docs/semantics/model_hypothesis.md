# Model hypothesis

## Vocabulary and boundary

The simulation models the recurring responsibilities of one condominium. Its
boundary ends at external payment processing, identity providers, devices, and
notification delivery. Those are represented only as deterministic pressures
or fake effects when needed.

## Candidate entities

- `Condominium`: the simulated tenant and its units.
- `Resident`: a person associated with a unit during a time interval.
- `PaymentObligation`: an amount due by a unit, paid through an external handoff.
- `MaintenanceRequest`: a resident-reported issue with a manager-owned lifecycle.
- `Announcement`: time-bounded information published by the manager.
- `StatusSummary`: the small set of items that currently require attention.

## Initial transitions

Payment obligations move `pending -> overdue` when time passes the due date and
`pending|overdue -> paid` when the external handoff is confirmed.

Maintenance requests move `submitted -> under_review -> planned -> in_progress
-> resolved`. Rejection is terminal for this first hypothesis.

## Initial invariants

- a resident sees obligations only for units to which they are currently
  associated;
- late obligations are actionable status items but do not each force a
  notification;
- every maintenance transition has an actor and simulated timestamp;
- resolved requests do not silently reopen;
- status summaries contain actionable items before historical detail;
- simulated time is timezone-aware and deterministic.

## Open questions

- When should an overdue obligation notify rather than only appear in status?
- How many open maintenance requests can a manager handle before escalation?
- Does a shared unit need one notification or one per resident?
- What does a resident need to see after moving units?
