# Refinement check 017

The simulation now has a repository-owned deterministic run tool. It executes
the same MRL Runtime adapter used by supervision and writes JSONL observations,
making scenario evidence durable and inspectable without changing domain
behavior.

The refinement makes invariant failure part of the tool exit contract: a log
is still preserved, but a failed scenario cannot be mistaken for a passing
validation command.
