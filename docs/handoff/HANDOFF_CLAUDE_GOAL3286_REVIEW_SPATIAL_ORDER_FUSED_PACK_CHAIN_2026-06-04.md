# Handoff To Claude: Goal3286 Review Spatial Ordering And Fused Segment Pack Chain

Please perform an independent read-only review of the recent RayJoin locality
and segment-packing chain. Write the review to:

`docs/reviews/goal3286_claude_review_spatial_order_and_fused_pack_chain_2026-06-04.md`

## Scope To Review

Review the current `main` branch, especially these goals and artifacts:

- Goal3278: RayJoin PIP point-order locality probe.
- Goal3280: generic `spatial_order_points_2d` helper and discovery exposure.
- Goal3282: generic `spatial_order_segments_2d` helper and LSI segment-order pod probe.
- Goal3284: NumPy/accessor fast-path retest for spatial ordering.
- Goal3285: fused `pack_segments(..., order_mode=...)`, runner timing, and pod evidence.

Key files:

- `src/rtdsl/spatial_order.py`
- `src/rtdsl/embree_runtime.py`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/primitive_hierarchy.py`
- `docs/rtdl_primitive_catalog.md`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py`
- `tests/goal3280_spatial_order_points_2d_generic_helper_test.py`
- `tests/goal3282_spatial_order_segments_2d_lsi_probe_test.py`
- `tests/goal3285_fused_segment_pack_order_mode_test.py`
- `tests/goal3285_fused_segment_pack_ordering_pod_evidence_test.py`
- `docs/reports/goal3280_spatial_order_points_2d_generic_helper_2026-06-03.md`
- `docs/reports/goal3282_spatial_order_segments_2d_lsi_probe_2026-06-03.md`
- `docs/reports/goal3284_numpy_spatial_order_fast_path_and_lsi_retest_2026-06-04.md`
- `docs/reports/goal3285_fused_segment_pack_ordering_rayjoin_lsi_probe_2026-06-04.md`
- `docs/reports/goal3285_fused_pack_lsi_segment_order_pod/*.json`

## Review Questions

1. Does the implementation keep native/runtime primitives app-agnostic? In
   particular, do `spatial_order_*` and `pack_segments(order_mode=...)` avoid
   RayJoin-specific semantics?
2. Is the Goal3285 conclusion correctly bounded: ordered layouts help the
   OptiX prepared query phase, but current host-side ordered packing is not a
   promoted high-performance RayJoin route?
3. Are the claim boundaries intact? Nothing should authorize release,
   RTDL-beats-RayJoin, RayJoin paper reproduction, true zero-copy, or broad
   RT-core speedup claims.
4. Are the tests and artifacts sufficient to support the internal engineering
   conclusion?
5. Is the recommended next engineering target correct: a generic
   packed/prepared column-layout or resident preprocessing primitive that avoids
   Python object reorder costs?

## Expected Verdict Values

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please lead with findings by severity, include concrete file/path references,
and state required-before-next-step versus optional follow-up work. Do not
modify source files; write only the review document.
