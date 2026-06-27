# Release-Facing Example Command Archive

Status: paused for V3 rebuild on 2026-06-20.

This page is not currently a release command archive. It previously pointed at
old tutorial paths and release wording that have now been quarantined.

## Current Safe Command

Development sanity only:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

This command does not certify V3 or authorize performance claims.

## Rebuild Requirement

A new release-facing command archive may be written only after the V3 rebuild
gate classifies exact rows as M7-qualified row-scoped and the aggregate release
gate authorizes publication. Each command must include:

- exact backend and partner;
- expected output contract;
- correctness signal;
- hardware when performance is discussed;
- artifact path for any timing claim.

Current authority:

- [V3 Rebuild Control](rebuild/v3/README.md)
- [Current Claim Boundaries](learn/current_claim_boundaries.md)
