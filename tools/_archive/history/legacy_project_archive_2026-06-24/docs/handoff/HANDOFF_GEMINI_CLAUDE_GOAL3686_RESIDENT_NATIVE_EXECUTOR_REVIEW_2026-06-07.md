# Handoff: Goal3686 Resident Native Scalar-Count Executor Review

Please review Goal3686 as an independent external reviewer.

## Files To Inspect

- `docs/reports/goal3686_resident_native_scalar_count_executor_2026-06-07.md`
- `docs/reports/goal3686_resident_native_scalar_count_executor_a5000/summary.json`
- `tests/goal3686_resident_native_scalar_count_executor_test.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py`

## Review Questions

1. Does the resident executor remain app-agnostic and generic?
2. Does it actually reuse native counter and launch-parameter buffers across runs?
3. Does it preserve the Goal3684 exact scalar-count contract and avoid dense boundary-row materialization?
4. Does the A5000 artifact support the narrow internal claim that the resident native executor is exact (`47262`) and faster than the resident Numba corrected path on the measured full public county dataset?
5. Are all claim boundaries intact: no release, default-route promotion, public speedup, RTDL-beats-RayJoin, RayJoin reproduction, broad RT-core speedup, or true-zero-copy authorization?

## Requested Output

Write a review to:

`docs/reviews/goal3687_<reviewer>_review_goal3686_resident_native_scalar_count_executor_2026-06-07.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please lead with findings by severity, then summarize evidence, tests, and any required next steps.
