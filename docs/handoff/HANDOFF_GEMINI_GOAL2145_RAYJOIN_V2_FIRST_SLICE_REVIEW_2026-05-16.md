# Gemini Handoff: Goal2145 RayJoin v2 First Slice Review

Please perform an independent Gemini review of Goal2145.

## Context

RTDL v2.0 is Python+partner+RTDL. The native RTDL engine must remain absolutely app-agnostic: no RayJoin-specific native ABI names, no GIS app-specific native hooks, and no domain-specific engine customization.

The user asked for a serious test/review/improvement path for implementing RayJoin-style workloads in RTDL v2 after reviewing the ICS 2024 paper "RayJoin: Fast and Precise Spatial Join." This goal is not a full paper reproduction. It is a first user-facing RTDL v2 slice for RayJoin-style PIP, LSI, and overlay-seed workloads.

## Files To Review

- `examples/rtdl_rayjoin_v2_spatial_join_app.py`
- `tests/goal2145_rayjoin_v2_spatial_join_app_test.py`
- `docs/reports/goal2145_rayjoin_v2_spatial_join_first_slice_2026-05-16.md`
- `tests/goal2145_rayjoin_v2_spatial_join_first_slice_report_test.py`

## Specific Questions

1. Does the app correctly use RTDL v2 generic primitives to express RayJoin-style PIP, LSI, and overlay-seed workloads without app-specific native engine customization?
2. Does the new PIP path correctly improve the first draft by using sparse `result_mode="positive_hits"` output instead of full-matrix post-filtering?
3. Are the claim boundaries in the report strict enough? In particular, it must not claim full RayJoin reproduction, paper-scale performance, conservative high-precision correctness, OptiX/RT-core evidence, or v2.0 release authorization.
4. Are the next-work items technically sensible: OptiX pod validation, derived scale datasets, CUDA/CuPy baselines, RayJoin repository adapter, and decision on point-location/closest-owner contract?
5. Do the tests guard the important behavior and documentation boundaries?

## Validation Already Run By Codex

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2145_rayjoin_v2_spatial_join_app_test tests.goal2145_rayjoin_v2_spatial_join_first_slice_report_test
py -3 -m py_compile examples\rtdl_rayjoin_v2_spatial_join_app.py tests\goal2145_rayjoin_v2_spatial_join_app_test.py tests\goal2145_rayjoin_v2_spatial_join_first_slice_report_test.py
$env:PYTHONPATH='src;.'; py -3 examples\rtdl_rayjoin_v2_spatial_join_app.py --workload all --backend cpu_python_reference --no-rows
$env:PYTHONPATH='src;.'; py -3 examples\rtdl_rayjoin_v2_spatial_join_app.py --workload all --backend embree --no-rows
```

The focused tests and CPU/Embree app runs passed locally.

## Required Output

Write your review to:

`docs/reviews/goal2146_gemini_review_goal2145_rayjoin_v2_first_slice_2026-05-16.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. Be explicit that this is an independent Gemini review distinct from Codex.
