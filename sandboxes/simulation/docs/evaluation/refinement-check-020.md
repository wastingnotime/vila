# Refinement check 020

The shared runtime now exercises maintenance status notification delivery after
the manager moves a request to `under_review`. Both residents of the addressed
unit receive one status item, while the manager payment policy remains grouped
and notification-silent for overdue obligations.

The refinement preserves per-recipient notification records in the runtime
projection in addition to aggregate counts.
