# Handoff: Goal2710 RayDB Native Device Hit-Stream Path Review

Please perform an independent read-only review of Goal2710.

## Files To Inspect

- `src/rtdsl/generic_primitives.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `tests/goal2710_raydb_native_device_hit_stream_path_test.py`
- `docs/reports/goal2710_raydb_native_device_hit_stream_path_2026-05-30.md`
- Immediate context:
  - `docs/reports/goal2706_native_optix_hit_stream_device_columns_2026-05-30.md`
  - `docs/reports/goal2708_hit_stream_cuda_array_torch_carrier_adapter_2026-05-30.md`
  - `docs/reviews/goal2709_gemini_review_goal2708_cuda_array_torch_carrier_adapter_2026-05-30.md`

## Review Questions

1. Does the new generic front door remain app-agnostic and OptiX-only/fail-closed
   rather than becoming a RayDB-specific API?
2. Does the RayDB benchmark path use native device hit-stream columns only for
   the intended OptiX/Triton non-reference path and preserve the old
   reference/host-row paths where needed?
3. Are claim boundaries preserved, especially no zero-copy/speedup claim before
   same-pointer/no-host-stage RTX pod evidence?
4. Are the no-pod tests and Windows/Linux focused validation sufficient for this
   wiring slice?

## Required Output

Write the review to:

`docs/reviews/goal2711_gemini_review_goal2710_raydb_native_device_hit_stream_path_2026-05-30.md`

Use one of these verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.
