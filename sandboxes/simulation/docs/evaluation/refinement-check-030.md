# Refinement check 030

The runtime now exercises resident departure after later queue activity. The
resident loses current access while historical activity remains queryable and
is emitted as departure-specific runtime evidence.

The refinement verifies departure correlation and confirms membership closure is
observed before the historical projection.
