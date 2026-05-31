# Gemini Review Task: Goal2812 RTNN Prepared-Query Aggregate Residency

Please perform an independent read-only review of Goal2812.

## Files To Inspect

- `docs/reports/goal2812_rtnn_prepared_query_aggregate_2026-05-31.md`
- `tests/goal2812_rtnn_prepared_query_aggregate_test.py`
- `docs/reports/goal2812_rtnn_prepared_query_aggregate_pod/rtnn_prepared_query_median_f32_32768.json`
- `docs/reports/goal2812_rtnn_prepared_query_aggregate_pod/rtnn_prepared_query_median_f32_65536.json`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `scripts/goal2800_rtnn_v25_live_ranked_summary_harness.py`
- `docs/reports/goal2811_rtnn_density_aware_direct_aggregate_2026-05-31.md`

## Questions

1. Confirm whether Goal2812 adds a generic prepared-query device-residency contract for fixed-radius 3D ranked aggregates, not an RTNN-specific shortcut.
2. Confirm whether the Python API and C ABI lifetimes are explicit enough: prepare query handle, aggregate with prepared search+prepared queries, destroy query handle.
3. Confirm whether the canonical RTNN harness uses the prepared-query mode and records median timing while preserving raw runs.
4. Confirm whether the pod artifacts are valid, clean-provenance, query-resident (`upload_sec: 0.0`), and still match the CuPy grid aggregate exactly.
5. Confirm whether the report presents the performance honestly: strong sparse-row improvement, near-neutral dense clustered improvement, 65K shell near parity, but CuPy remains faster and no public speedup claim is authorized.
6. Call out any stale wording, overclaim, missing evidence, lifecycle risk, or test/report mismatch.

## Expected Output

Write your review to:

`docs/reviews/goal2812_gemini_review_rtnn_prepared_query_aggregate_2026-05-31.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

This is not a release review and should not be treated as v2.5 release consensus.
