# Gemini Handoff: Goal2147 RayJoin v2 Scale Harness Review

Please perform an independent Gemini review of Goal2147.

## Context

Goal2145 added a first user-facing RTDL v2 RayJoin-style app for PIP, LSI, and overlay-seed workloads. Gemini reviewed Goal2145 as `accept-with-boundary`.

Goal2147 extends that work by adding a deterministic scale/perf harness and correcting the overlay contract wording. The native engine must remain app-agnostic. This goal must not claim full RayJoin reproduction, paper-scale performance, RT-core speedup, or v2.0 release readiness.

## Files To Review

- `examples/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal2147_rayjoin_v2_scale_perf.py`
- `docs/reports/goal2147_rayjoin_v2_scale_perf_harness_2026-05-16.md`
- `docs/reports/goal2147_rayjoin_v2_scale_perf_quick_local_2026-05-16.json`
- `tests/goal2147_rayjoin_v2_scale_perf_test.py`
- Updated Goal2145 report/tests for the overlay wording correction:
  - `docs/reports/goal2145_rayjoin_v2_spatial_join_first_slice_2026-05-16.md`
  - `tests/goal2145_rayjoin_v2_spatial_join_app_test.py`
  - `tests/goal2145_rayjoin_v2_spatial_join_first_slice_report_test.py`

## Specific Questions

1. Is the overlay wording correction technically right? The app should describe overlay output as `overlay_pair_dependency_rows_with_lsi_pip_flags`, with active continuation seeds derived from `requires_lsi` / `requires_pip`, not as only active seed rows.
2. Does the scale harness generate meaningful deterministic synthetic workloads for PIP, LSI, and overlay without adding app-specific native engine hooks?
3. Are progress logs sufficient for long-running medium/large runs?
4. Are the claim boundaries strict enough? No full RayJoin reproduction, no paper-scale performance, no RT-core speedup claim, no v2 release authorization.
5. Is the next-work plan sensible: OptiX pod runs, CUDA/CuPy baselines, RayJoin repository adapter outside the engine, and point-location/closest-owner contract decision?

## Validation Already Run By Codex

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2145_rayjoin_v2_spatial_join_app_test tests.goal2145_rayjoin_v2_spatial_join_first_slice_report_test tests.goal2146_gemini_review_goal2145_rayjoin_v2_first_slice_test tests.goal2147_rayjoin_v2_scale_perf_test
py -3 -m py_compile examples\rtdl_rayjoin_v2_spatial_join_app.py scripts\goal2147_rayjoin_v2_scale_perf.py tests\goal2147_rayjoin_v2_scale_perf_test.py tests\goal2145_rayjoin_v2_spatial_join_app_test.py tests\goal2145_rayjoin_v2_spatial_join_first_slice_report_test.py
$env:PYTHONPATH='src;.'; py -3 scripts\goal2147_rayjoin_v2_scale_perf.py --scale quick --backends cpu,embree --repeats 2 --warmups 0 --output docs\reports\goal2147_rayjoin_v2_scale_perf_quick_local_2026-05-16.json
```

## Required Output

Write your review to:

`docs/reviews/goal2148_gemini_review_goal2147_rayjoin_scale_harness_2026-05-16.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. State explicitly that this is an independent Gemini review distinct from Codex.
