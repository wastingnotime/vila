# Refinement check 022

The shared runtime now exercises a manual payment handoff. A manager confirms
one local obligation as paid, runtime evidence records the intention, command,
domain event, and projection, and overdue count decreases from three to two.
No payment provider or card data is introduced.

The build also exposed and corrected historical payment evaluation: a payment
confirmed later remains overdue in summaries before its confirmation timestamp,
but not after it.

Payment confirmation now checks a supplied actor's manager role, and runtime
evidence includes the payment index, resulting status, and paid timestamp.
