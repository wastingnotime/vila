# Refinement check 068

Maintenance notification lookup rejects an unknown request reference with a
stable domain error instead of leaking a dictionary lookup failure.
