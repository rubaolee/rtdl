# External Review Handoff: Goals3441-3443 RayJoin Active-Count Device Continuation

Please perform an independent review of the Goal3441-3443 chain on current `main`.

## Context

This chain improves the Spatial RayJoin overlay active-count reference route while keeping the native engine app-agnostic.

- Goal3441 added generic phase telemetry for prepared OptiX shape-pair active-count.
- Goal3442 added an opt-in generic device-side active-count continuation:
  - existing OptiX shape-pair traversal writes generic segment-intersection flags on device;
  - a generic CUDA continuation computes inclusive first-vertex containment and scalar active count on device;
  - only the scalar count is copied back.
- Goal3443 promoted that device continuation to the default app-layer overlay active-count reference route while preserving `run_packed_left_host_exact(...)` as the oracle/debug path.

## Files To Inspect

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `scripts/goal3441_shape_pair_active_count_phase_timing_probe.py`
- `scripts/goal3442_shape_pair_active_count_device_continuation_probe.py`
- `scripts/goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py`
- `tests/goal3441_shape_pair_active_count_phase_timings_test.py`
- `tests/goal3442_shape_pair_active_count_device_continuation_test.py`
- `tests/goal3443_spatial_rayjoin_overlay_active_count_device_default_test.py`
- `docs/reports/goal3441_shape_pair_active_count_phase_timings_2026-06-05.md`
- `docs/reports/goal3442_shape_pair_active_count_device_continuation_2026-06-05.md`
- `docs/reports/goal3443_spatial_rayjoin_overlay_active_count_device_default_2026-06-05.md`
- Pod artifacts:
  - `docs/reports/goal3441_shape_pair_active_count_phase_timings_pod_2026-06-05.json`
  - `docs/reports/goal3442_shape_pair_active_count_device_continuation_pod_2026-06-05.json`
  - `docs/reports/goal3443_spatial_rayjoin_overlay_active_count_device_default_pod_2026-06-05.json`

## Questions

1. Does the native implementation remain app-agnostic, with no RayJoin/CDB/county/soil semantics inside the engine?
2. Is the device-continuation correctness evidence sufficient for the current v2.8 benchmark input: host exact counts `[4543, 4543, 4543, 4543]`, device counts `[4543, 4543, 4543, 4543]`, `all_counts_match: true`?
3. Was the initial 4-count mismatch handled correctly by adding inclusive point-on-boundary semantics before parity?
4. Is the default promotion in Goal3443 justified while preserving `run_packed_left_host_exact(...)` as the explicit oracle/debug path?
5. Are the timing interpretations honest: Goal3441 host median about `0.147s`, Goal3442 device warm median about `0.00644s`, Goal3443 default overlay warm median about `0.00546s`, with cold first iteration disclosed?
6. Are all claim boundaries still closed: no release authorization, no public speedup claim, no RayJoin reproduction claim, no RT-core speedup claim, no true zero-copy claim?
7. Any bugs, missing tests, schema drift, API naming risk, or wording risk before the next v2.8 step?

## Expected Output

Write your review to one of:

- Claude: `docs/reviews/goal3444_claude_review_goals3441_3443_rayjoin_active_count_device_continuation_2026-06-05.md`
- Gemini: `docs/reviews/goal3445_gemini_review_goals3441_3443_rayjoin_active_count_device_continuation_2026-06-05.md`

Use verdict `accept`, `accept-with-boundary`, `reject`, or `needs-more-evidence`.
