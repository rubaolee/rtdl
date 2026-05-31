# Gemini Review Task: Goal2810 RTNN Ranked-Summary Aggregate

Please perform an independent read-only review of Goal2810.

## Files To Inspect

- `docs/reports/goal2810_rtnn_ranked_summary_aggregate_2026-05-31.md`
- `tests/goal2810_rtnn_ranked_summary_aggregate_test.py`
- `docs/reports/goal2810_rtnn_ranked_summary_aggregate_pod/rtnn_aggregate_f32_32768.json`
- `docs/reports/goal2810_rtnn_ranked_summary_aggregate_pod/rtnn_aggregate_f32_65536.json`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py`
- `tests/goal2800_rtnn_v25_live_ranked_summary_harness_test.py`
- `tests/goal2384_prepared_3d_neighbor_ranked_summary_test.py`

## Questions

1. Confirm whether Goal2810 adds a generic prepared fixed-radius ranked-neighbor aggregate path, not an RTNN-specific native engine shortcut.
2. Confirm whether the clean pod artifacts are valid, clean-provenance, and show exact candidate-count and aggregate-summary agreement with the CuPy grid opponent.
3. Confirm whether the report correctly presents the performance result: RTDL improved materially over the previous ranked-row path, but CuPy remains faster, so no public speedup claim is authorized.
4. Confirm whether the float32 comparison boundary is explicit and fair because the promoted CuPy grid opponent is float32, while the exact-double aggregate path remains available.
5. Confirm whether the tests cover the native/Python surfaces, pod artifacts, claim boundary, and remaining-work explanation.
6. Call out any stale wording, overclaim, missing evidence, or test/report mismatch.

## Expected Output

Write your review to:

`docs/reviews/goal2810_gemini_review_rtnn_ranked_summary_aggregate_2026-05-31.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is not a release review and should not be treated as v2.5 release consensus.
