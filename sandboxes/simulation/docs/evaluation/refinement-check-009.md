# Refinement check 009

The maintenance queue run produces manager-attention backlog `[2, 4, 6]` when
two requests arrive per month and one is advanced by the manager. The
`under_review` request remains attention-worthy, matching the manager status
projection. This makes pressure observable without pretending that a staffing
or escalation policy has already been validated.
