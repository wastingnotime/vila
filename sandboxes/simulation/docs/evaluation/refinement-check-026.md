# Refinement check 026

The runtime now traces manager-owned status inputs: delivery receipt and
announcement publication each have an intention and domain-event observation
before the composed status projections.

The refinement verifies stable correlation IDs and subject identifiers on both
domain-event observations.
