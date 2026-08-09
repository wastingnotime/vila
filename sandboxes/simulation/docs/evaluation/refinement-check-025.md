# Refinement check 025

The runtime now emits resident activity after manual payment confirmation. The
projection contains the plain-language payment activity, addressed unit, and
simulated confirmation timestamp.

The projection preserves earlier overdue and maintenance entries and appends
the paid activity, matching the append-only history model.

The runtime action boundaries were also corrected so manager review, delivery
collection, payment confirmation, and paid-activity projection execute as
separate scheduled actions in chronological order.

The refinement adds ordering assertions for maintenance notification delivery,
delivery collection, and payment activity projection.
