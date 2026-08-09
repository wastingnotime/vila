# Refinement check 002

The notification-fatigue slice supports the current hypothesis: three overdue
payments remain visible in the manager status, while one submitted maintenance
request produces one daily actionable notification. Repeating the status query
does not duplicate it.

This is a simulation policy, not a production notification contract. The next
refinement adds a second resident to unit 101. Both residents see the same
unit-level status items, so the current model does not duplicate payment or
maintenance state per person. Recipient-level notification policy remains open.
