# Refinement check 011

The role-boundary slice makes the resident/manager distinction executable:
residents can submit maintenance requests, managers can advance them, and
unknown or incorrectly acting identities are rejected before event recording.

The refinement makes the manager check a named authorization boundary and
proves denied resident and manager commands leave the event stream unchanged.
