# Review Debt: V4 Tier-3 OptiX Module-Link Probe

Date: 2026-06-24

Status: recorded review debt, not release authorization.

## Why This Debt Exists

The module-link probe is a boundary-sensitive negative result. It shows that Numba PTX generation is not enough for OptiX acceptance: direct `optixModuleCreate` on bare helper PTX failed because the module has no OptiX semantic entry functions.

This should receive external review before any stronger Tier-3 callback claim is made.

## Current Evidence

- POD evidence: `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json`
- Status: `blocked`
- Blocked stage: `optix_module_create`
- `ptx_generated`: `true`
- `optix_module_link_attempted`: `true`
- `optix_module_link_succeeded`: `false`
- `program_group_create_attempted`: `false`
- `pipeline_launch_attempted`: `false`
- `tier3_callback_claim_authorized`: `false`
- `raw_optix_callback_claim_authorized`: `false`
- `release_claim_authorized`: `false`

## Required External Review

Review packet:

- `future/v4/reviews/call_for_review_v4_tier3_optix_module_link_probe_2026-06-24.md`

Required reviewer focus:

1. Confirm the negative result is interpreted honestly.
2. Confirm that Tier-3 remains V4.x spike territory, not V4.0 support.
3. Confirm that the next valid step is wrapper/direct-callable ABI evidence, not public callback API exposure.

## Non-Authorization

This debt record does not authorize V4 release, Tier-3 callback support, raw OptiX callback API support, broad V4 speedup claims, app-specific native kernels, or movement of Tier-3 into the V4.0 release surface.
