# Review Debt: V4 Tier-3 Numba PTX Probe

Date: 2026-06-24

Status: recorded review debt, not release authorization.

## Why This Debt Exists

The Tier-3 Numba PTX probe is intentionally narrow but boundary-sensitive. It proves only that a scalar Numba CUDA device function can generate PTX on the POD. It does not prove OptiX module linking, callable overhead, traversal integration, correctness inside OptiX, or public callback support.

This should receive external review before any stronger claim is made.

Claude review was not retried at creation time because the previously observed session reset was still pending. This debt is recorded so engineering can continue without waiting on reviewer availability.

## Current Evidence

- POD evidence: `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json`
- Status: `ptx_generated`
- `ptx_generated`: `true`
- `cuda_available`: `true`
- `optix_module_link_attempted`: `false`
- `tier3_callback_claim_authorized`: `false`
- `raw_optix_callback_claim_authorized`: `false`
- `release_claim_authorized`: `false`

## Required External Review

Review packet:

- `future/v4/reviews/call_for_review_v4_tier3_numba_ptx_probe_2026-06-24.md`

Required reviewer focus:

1. Confirm that this is only Tier-3 spike evidence.
2. Confirm that no V4.0 release feature is implied.
3. Confirm that the next valid engineering step is OptiX module-link spike evidence, not public API exposure.

## Non-Authorization

This debt record does not authorize V4 release, Tier-3 callback support, raw OptiX callback API support, broad V4 speedup claims, app-specific native kernels, or movement of Tier-3 into the V4.0 release surface.
