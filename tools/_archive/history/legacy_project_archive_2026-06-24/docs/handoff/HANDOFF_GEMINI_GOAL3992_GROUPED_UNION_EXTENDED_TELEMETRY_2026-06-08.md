# Handoff: Gemini Review For Goal3992 Grouped-Union Extended Telemetry

Please perform an independent read-only review of Goal3992.

## Files To Read

- `docs/reports/goal3992_grouped_union_extended_telemetry_2026-06-08.md`
- `docs/reports/goal3992_grouped_union_extended_telemetry_pod_smoke.json`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3992_grouped_union_extended_telemetry_pod_smoke.py`
- `tests/goal3992_grouped_union_extended_telemetry_contract_test.py`

## Review Questions

1. Does the new extended telemetry path preserve the old 4-counter ABI and only write counters 4-7 when an explicit telemetry count permits it?
2. Does the Python runtime correctly select the extended symbol only for an 8+ counter telemetry buffer while preserving the old path for 4-counter buffers?
3. Does the pod artifact actually prove the extended symbol executed and produced useful generic candidate/root-read telemetry?
4. Does the report avoid overclaiming performance, release readiness, broad RT-core speedup, whole-app speedup, true-zero-copy, automatic partner selection, or app-specific engine logic?
5. Are the new counter names app-agnostic and useful for the next dense grouped-union primitive design?

## Required Output

Write the review to:

`docs/reviews/goal3993_gemini_review_goal3992_grouped_union_extended_telemetry_2026-06-08.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

