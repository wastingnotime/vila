# Slice: maintenance response queue

## Use-case contract

Over three simulated months, two maintenance requests arrive each month while
the manager advances one request to `under_review`. The submitted-review queue
therefore grows from one to three.

## Hypothesis under test

Status visibility makes pressure measurable, but it does not remove work by
itself. If request arrivals exceed manager response capacity, the simulation
should expose the queue growth so a later refinement can test escalation or
workflow changes.

## Done criteria

- request arrivals and manager responses are deterministic;
- queue size is measured after each monthly response window;
- transitions retain their manager actor and simulated timestamp;
- no escalation policy is invented before queue evidence exists.

## Out of scope

SLA promises, automatic assignment, contractor scheduling, escalation rules,
severity scoring, and staffing optimization.
