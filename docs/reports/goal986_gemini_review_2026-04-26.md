# Goal986 Gemini Review: Road-Hazard Threshold-Count Continuation

Date: 2026-04-26

## Decision: ACCEPT

### Reasons for Acceptance:

1.  **`count_at_least` API is Correctly Wired:**
    *   The `PreparedOptixSegmentPolygonHitcount2D.count_at_least` method in `src/rtdsl/optix_runtime.py` is implemented with robust input validation (non-negative threshold, uint32 range) and correct handling for empty input scenes.
    *   The Python method correctly interfaces with the native `rtdl_optix_count_prepared_segment_polygon_hitcount_at_least_2d` function, which is properly declared in `src/native/optix/rtdl_optix_prelude.h` and implemented in `src/native/optix/rtdl_optix_api.cpp`, delegating to a `PreparedSegmentPolygonHitcount2D` implementation in `src/native/optix/rtdl_optix_workloads.cpp`.
    *   Unit tests in `tests/goal933_prepared_segment_polygon_optix_test.py` confirm the behavior of empty scenes, threshold validation, and closed handle rejection, verifying the API's correctness and robustness.

2.  **`road_hazard_prepared_summary` Avoids Row Materialization in Warm Query Samples:**
    *   The `_profile_road_hazard` function within `scripts/goal933_prepared_segment_polygon_optix_profiler.py` explicitly calls `prepared.count_at_least()` for warm query samples, rather than `prepared.run()`.
    *   The `python_postprocess_sec` is deliberately set to `None`, indicating no post-processing of materialized rows.
    *   The test `test_road_run_profile_uses_threshold_count_not_row_materialization` in `tests/goal933_prepared_segment_polygon_profiler_test.py` uses a mock to confirm that `prepared.run()` is not invoked, while `count_at_least()` is. This confirms the avoidance of row materialization for the compact summary path.

3.  **Validation Semantics are Still Honest for Compact Summary:**
    *   The profiler in `scripts/goal933_prepared_segment_polygon_optix_profiler.py` accurately calculates `expected_priority_count` from the CPU reference (`road_app.road_hazard_hitcount`) by summing segments with a hit count of 2 or more.
    *   This `expected_priority_count` is then directly compared against `last_priority_count` obtained from the `count_at_least` API. This direct scalar-to-scalar comparison ensures that the validation of the compact summary remains honest and accurate.

4.  **Public RTX Speedup Claims Remain Unauthorized:**
    *   The `docs/reports/goal986_road_hazard_threshold_count_continuation_2026-04-26.md` explicitly states: "It does not authorize public RTX speedup claims." and lists specific disclaimers.
    *   The profiler (`scripts/goal933_prepared_segment_polygon_optix_profiler.py`) includes `non_claim` and `boundary` fields in its output JSON that explicitly reiterate that this work does not constitute a public speedup claim for the broader application.
    *   The `docs/app_engine_support_matrix.md` consistently classifies `road_hazard_screening` as `optix_traversal_prepared_summary` and indicates `ready_for_rtx_claim_review` for a *sub-path* with clear notes that no full application speedup is claimed or authorized. This aligns with the conservative approach to RTX claims.

The implementation and documentation align with the stated goals and constraints, ensuring that the new `count_at_least` API is correctly integrated and that no unauthorized speedup claims are made.
