# Refinement check 005

The activity-history slice keeps the primary status use case concise while
providing supporting context. Residents see only current-unit activity, while
the manager sees condominium activity. The projection translates domain events
into plain-language summaries and does not expose technical event names.

The initial run also confirmed that payment activity should be ordered by the
obligation due date rather than by the later read-time projection event.

The refinement separates status from history: after moving units, a resident's
current status follows the new unit, while their activity history retains
events from units present in their membership history. A later departure can
therefore preserve personal history without preserving current-unit access.
