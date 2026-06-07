# Handoff: Goal3684 Native Relation-Status Corrected Scalar Count Review

Please review Goal3684 as an independent external reviewer.

## Files To Inspect

- `docs/reports/goal3684_native_relation_status_corrected_scalar_count_2026-06-07.md`
- `docs/reports/goal3684_native_relation_status_corrected_scalar_count_a5000/summary.json`
- `tests/goal3684_native_relation_status_corrected_scalar_count_test.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py`

## Review Questions

1. Does the new native ABI remain app-agnostic, with no RayJoin/CDB/county/GIS-specific contract in the engine?
2. Does the implementation actually avoid dense boundary-row materialization for the scalar count route?
3. Is the double-precision boundary-correction logic consistent with the existing exact Numba boundary-contact contract?
4. Does the A5000 artifact support the narrow claim that the native scalar route is exact (`47262`) and faster than the resident Numba corrected path on the measured full public county dataset?
5. Are all claim boundaries intact: no release, default-route, public speedup, RTDL-beats-RayJoin, RayJoin reproduction, broad RT-core speedup, or true-zero-copy authorization?

## Requested Output

Write a review to:

`docs/reviews/goal3685_<reviewer>_review_goal3684_native_relation_status_corrected_scalar_count_2026-06-07.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please lead with findings by severity, then summarize the evidence and any required next steps.
