# Refinement check 008

The monthly-obligation run shows queue growth when one unit remains unpaid:
manager overdue pressure is `[1, 2, 3]` across three months while six of nine
obligations are manually marked paid. This provides a bounded time-series
pressure scenario without turning the simulation into accounting software.

The refinement bounds this scenario to one through twelve months, preventing
empty runs and invalid month arithmetic from being mistaken for evidence.
