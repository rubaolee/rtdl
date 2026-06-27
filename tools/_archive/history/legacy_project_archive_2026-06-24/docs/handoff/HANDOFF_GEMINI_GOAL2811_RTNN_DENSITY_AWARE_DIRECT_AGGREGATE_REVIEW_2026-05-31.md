# Gemini Review Task: Goal2811 RTNN Density-Aware Direct Aggregate

Please perform an independent read-only review of Goal2811.

## Files To Inspect

- `docs/reports/goal2811_rtnn_density_aware_direct_aggregate_2026-05-31.md`
- `tests/goal2811_rtnn_direct_aggregate_kernel_test.py`
- `docs/reports/goal2811_rtnn_direct_density_aggregate_pod/rtnn_direct_density_median_f32_32768.json`
- `docs/reports/goal2811_rtnn_direct_density_aggregate_pod/rtnn_direct_density_median_f32_65536.json`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py`
- `docs/reports/goal2810_rtnn_ranked_summary_aggregate_2026-05-31.md`

## Questions

1. Confirm whether Goal2811 remains a generic fixed-radius ranked-neighbor aggregate improvement, not an RTNN-specific native engine shortcut.
2. Confirm whether the density-aware selection is reasonable: direct one-kernel aggregate for low occupied-cell density and two-step aggregate for dense clustered rows.
3. Confirm whether the harness change from last-run timing to median repeat timing is correct and makes the evidence more stable without hiding raw runs.
4. Confirm whether the clean pod artifacts are valid, clean-provenance, and keep exact candidate-count and aggregate-summary agreement with the CuPy grid opponent.
5. Confirm whether the report presents the performance honestly, including the small 65K shell regression and the fact that CuPy remains faster on all rows.
6. Call out any stale wording, overclaim, missing evidence, or test/report mismatch.

## Expected Output

Write your review to:

`docs/reviews/goal2811_gemini_review_rtnn_density_aware_direct_aggregate_2026-05-31.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is not a release review and should not be treated as v2.5 release consensus.
