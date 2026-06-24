# Handoff: Goal3688 Native-PIP RayJoin Composite Review

Please perform a read-only independent review of Goal3688 and write your review to:

`docs/reviews/goal3689_gemini_review_goal3688_native_pip_safe_mixed_composite_2026-06-07.md`

## Context

Goal3688 tests whether the Goal3686 generic resident native scalar-count executor can replace the older CuPy PIP correction leg inside the current safe RayJoin count composite.

It does not change the rest of the composite:

- PIP: native resident relation-status corrected scalar count,
- LSI: existing exact prepared RTDL/OptiX route with host double refinement,
- overlay seed: existing RTDL/OptiX active-count route.

This is an internal candidate route only. Do not authorize release, default-route promotion, public speedup claims, RayJoin paper reproduction claims, RTDL-beats-RayJoin claims, broad RT-core claims, or true-zero-copy claims.

## Files To Inspect

- `docs/reports/goal3688_rayjoin_native_pip_safe_mixed_composite_2026-06-07.md`
- `docs/reports/goal3688_rayjoin_native_pip_safe_mixed_composite_a5000/summary.json`
- `scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py`
- `tests/goal3688_rayjoin_native_pip_safe_mixed_composite_test.py`
- `docs/research/future_version_to_do_list.md`

You may also inspect supporting Goal3684/Goal3686 native executor code if needed:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `tests/goal3686_resident_native_scalar_count_executor_test.py`

## Questions To Answer

1. Does Goal3688 preserve app-agnostic native-engine boundaries, with no RayJoin/CDB/county/GIS-specific native ABI or hidden app policy?
2. Does the runner honestly compare the candidate composite against the dense all-CuPy same-contract baseline and fail closed on count mismatch?
3. Is the A5000 artifact credible for the limited internal conclusion, including source-scoped clean status, exact count parity, and the `205.372x` composite speedup versus dense all-CuPy for the measured 4096-chain packet?
4. Does the report avoid overclaiming release readiness, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, and true zero-copy?
5. Are there any required fixes before this candidate route can be considered for internal benchmark-summary promotion?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
