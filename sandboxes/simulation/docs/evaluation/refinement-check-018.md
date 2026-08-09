# Refinement check 018

The shared runtime scenario now emits notification-policy evidence. At the
summary instant, three overdue payments remain visible in manager status but do
not generate payment notifications; the submitted maintenance request produces
one actionable `maintenance_review_required` notification.

The refinement preserves grouped item counts in the runtime projection, so
notification aggregation can be inspected independently from notification
kind.
