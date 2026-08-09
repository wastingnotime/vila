# Refinement check 019

The shared runtime scenario now emits role-scoped activity history alongside
status summaries. Residents receive one unit's human-readable payment and
maintenance context, while the manager receives condominium-wide payment
context without raw event names.

The runtime payload now retains each entry's kind, subject ID, and simulated
timestamp in addition to its readable summary, making replay evidence precise
without changing the user-facing vocabulary.
