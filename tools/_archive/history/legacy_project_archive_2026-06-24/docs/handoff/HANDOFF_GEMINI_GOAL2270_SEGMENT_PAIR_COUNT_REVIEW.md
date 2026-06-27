# Gemini Review Task: Goal2270 Prepared Segment-Pair Count Probe

Please perform an independent read-only review of Goal2269/Goal2270.

## Files To Read

- `docs/reports/goal2269_prepared_segment_pair_intersection_count_mode_2026-05-17.md`
- `tests/goal2269_prepared_segment_pair_intersection_count_mode_test.py`
- `docs/reports/goal2270_prepared_segment_pair_count_probe_2026-05-17.md`
- `docs/reports/goal2270_prepared_segment_pair_count_probe_pod_2026-05-17.json`
- `tests/goal2270_prepared_segment_pair_count_probe_test.py`
- Relevant implementation:
  - `src/native/optix/rtdl_optix_workloads.cpp`
  - `src/native/optix/rtdl_optix_api.cpp`
  - `src/native/optix/rtdl_optix_prelude.h`
  - `src/rtdsl/optix_runtime.py`

## Review Questions

1. Confirm whether Goal2269 adds a generic count-only prepared segment-pair intersection API without introducing app-specific names or RayJoin/LSI-specific logic into the engine.
2. Confirm whether the count path preserves exactness by using the same candidate collection plus host exact `exact_segment_intersection` refinement and duplicate-pair suppression.
3. Confirm whether Goal2270's pod evidence supports only the narrow claim stated in the report: exact scalar count parity and larger-scale speedup versus raw witness-row return on synthetic crossing grids.
4. Check that the report does not overclaim whole-app speedup, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, or pure device-resident continuation.
5. Note any blocker or claim-boundary problem.

## Output

Write your review to:

`docs/reviews/goal2271_gemini_review_goal2269_2270_segment_pair_count_2026-05-17.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

