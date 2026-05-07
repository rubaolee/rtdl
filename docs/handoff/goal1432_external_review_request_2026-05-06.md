# Goal 1432 External Review Request: Production Wrapper Generic Symbol Route

Please review Goal1432 for RTDL v1.5.1 `COLLECT_K_BOUNDED`.

## Question

Can we accept this as evidence that the Embree and OptiX production Python wrappers now route native candidate rows through the built app-name-free generic i64 symbols, while still blocking stable primitive promotion, speedup wording, zero-copy wording, whole-app behavior, broad workload claims, and release action?

## Files To Review

- Contract: `src/rtdsl/v1_5_1_collect_k_bounded.py`
- Embree wrapper: `src/rtdsl/embree_runtime.py`
- OptiX wrapper: `src/rtdsl/optix_runtime.py`
- Summary: `docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_route_2026-05-06.md`
- Linux Embree report: `docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_linux_embree_2026-05-06.md`
- RTX A5000 pod OptiX report: `docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_pod_optix_2026-05-06.md`
- Guard test: `tests/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_test.py`

## Local Validation

- Windows focused slice: `Ran 45 tests OK`
- Linux focused slice: `Ran 45 tests OK`
- Linux Embree measured wrapper route: `pass=4, fail=0, skipped=0`
- RTX A5000 pod OptiX measured wrapper route: `pass=4, fail=0, skipped=0`

## Claim Boundary To Check

This package should be accepted only as production-wrapper routing evidence for built generic i64 symbols. It must not be treated as stable `COLLECT_K_BOUNDED` promotion, performance evidence, zero-copy evidence, whole-app behavior evidence, broad workload evidence, or a release action.
