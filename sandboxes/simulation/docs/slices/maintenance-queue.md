# Slice: maintenance response queue

## Use-case contract

Over three simulated months, two maintenance requests arrive each month while
the manager advances one request to `under_review`. The manager-attention queue
therefore grows from two to six. Requests in `under_review` still require
manager attention until they are planned or otherwise closed.

## Hypothesis under test

Status visibility makes pressure measurable, but it does not remove work by
itself. If request arrivals exceed manager response capacity, the simulation
should expose the queue growth so a later refinement can test escalation or
workflow changes.

## Done criteria

- request arrivals and manager responses are deterministic;
- manager-attention queue size includes `submitted` and `under_review` states;
- transitions retain their manager actor and simulated timestamp;
- no escalation policy is invented before queue evidence exists.

## Out of scope

SLA promises, automatic assignment, contractor scheduling, escalation rules,
severity scoring, and staffing optimization.
