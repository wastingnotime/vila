# Refinement check 001

## Evidence

The first runtime execution produced the expected resident and manager status
projections and passed `status_has_actionable_items`. It also showed that the
scenario opened a request but never exercised the manager's first response,
although the slice contract said that behavior was in scope.

## Refinements

- Added a second scheduled action on 2026-01-07 for the manager to move the
  request from `submitted` to `under_review`.
- Added a replay test proving the event history rebuilds the same resident
  status projection.

## Result

The slice now covers the resident report, manager response, event history, and
status projection. Notification policy remains unresolved: the current model
still makes overdue status visible without emitting a notification.

## Next question

Compare the cost of a visible overdue item with a notification when the manager
queue contains multiple late obligations. This should be a separate scenario,
not an expansion of this slice's production surface.
