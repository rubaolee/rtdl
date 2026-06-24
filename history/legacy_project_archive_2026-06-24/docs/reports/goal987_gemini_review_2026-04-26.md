Goal987 Segment/Polygon Aggregate Continuation Review - Gemini Agent

Date: 2026-04-26

Review Status: ACCEPT

Concrete Reasons:

1.  **`aggregate()` wiring is correct:**
    *   The `PreparedOptixSegmentPolygonHitcount2D.aggregate` method in `src/rtdsl/optix_runtime.py` correctly calls the native `rtdl_optix_aggregate_prepared_segment_polygon_hitcount_2d` function via `ctypes`.
    *   The native ABI in `src/native/optix/rtdl_optix_prelude.h` declares the function, and `src/native/optix/rtdl_optix_api.cpp` provides its external linkage to an internal implementation (`aggregate_prepared_segment_polygon_hitcount_2d_optix`).
    *   The feature is appropriately used and tested in `scripts/goal933_prepared_segment_polygon_optix_profiler.py` and `tests/goal933_prepared_segment_polygon_profiler_test.py`.

2.  **Row materialization is avoided in warm query samples:**
    *   The documentation (`docs/reports/goal987_segment_polygon_aggregate_continuation_2026-04-26.md`) clearly states that `prepared.aggregate(...)` is used, replacing `prepared.run(...)` for warm query samples, thus avoiding row materialization.
    *   This is confirmed by the implementation in `scripts/goal933_prepared_segment_polygon_optix_profiler.py` in the `_profile_segment_hitcount` function, which explicitly calls `prepared.aggregate` for warm queries.
    *   This behavior is also verified by `tests/goal933_prepared_segment_polygon_profiler_test.py` through the `test_segment_run_profile_uses_native_aggregate_not_row_materialization` test.

3.  **Digest validation remains honest:**
    *   The `_profile_segment_hitcount` function in `scripts/goal933_prepared_segment_polygon_optix_profiler.py` includes robust validation logic. When `skip_validation` is false, it computes an `expected_digest` from a CPU reference (`rt.run_cpu_python_reference`) and compares it against the `last_digest` obtained from the native aggregate.
    *   The `_digest` helper function ensures a consistent and normalized comparison by sorting and summing hit counts.

4.  **Public RTX speedup claims remain unauthorized:**
    *   The `Goal987` documentation (`docs/reports/goal987_segment_polygon_aggregate_continuation_2026-04-26.md`) explicitly states that this work "does not authorize public RTX speedup claims."
    *   The profiler script (`scripts/goal933_prepared_segment_polygon_optix_profiler.py`) further reinforces this with its `cloud_claim_contract` and `boundary` sections, which explicitly state that public speedup claims require further review and comparison with baselines.
    *   The `docs/app_engine_support_matrix.md` consistently classifies the `segment_polygon_hitcount` app with an `optix_traversal_prepared_summary` performance class, and the RT-Core App Maturity Contract notes for this app explicitly limit public wording to compact hit-count traversal, preventing over-authorization of speedup claims.

Overall, the implementation aligns with the stated objectives, adheres to established technical wiring patterns, and maintains a conservative and honest stance on performance claims, consistent with project standards.
