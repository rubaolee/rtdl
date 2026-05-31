# Handoff: Gemini Review For Goal2817 RTNN Block-Partial Aggregate

Please perform an independent read-only Gemini review of Goal2817 and write the
review to:

`docs/reviews/goal2817_gemini_review_rtnn_block_partial_aggregate_2026-05-31.md`

## Context

Goal2817 is a v2.5 RTNN fixed-radius ranked-summary runtime improvement. It
adds a generic block-partial variant for prepared-query, summary-only float32
fixed-radius aggregates. Each CUDA block writes one `FrnRankedAggregate`
partial into a prepared query-owned workspace; the host downloads and reduces
those small partials. This is intended to reduce small-row aggregate traffic
without introducing any RTNN-specific native ABI or benchmark-specific native
logic.

## Files To Inspect

- `docs/reports/goal2817_rtnn_block_partial_aggregate_2026-05-31.md`
- `tests/goal2817_rtnn_block_partial_aggregate_test.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `docs/reports/goal2817_rtnn_block_partial_aggregate_pod/rtnn_block_partial_median_f32_32768.json`
- `docs/reports/goal2817_rtnn_block_partial_aggregate_pod/rtnn_block_partial_median_f32_65536.json`
- Comparison context:
  - `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_2026-05-31.md`
  - `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_pod/rtnn_workspace_median_f32_32768.json`
  - `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_pod/rtnn_workspace_median_f32_65536.json`

## Review Questions

1. Confirm whether Goal2817 is generic and app-agnostic: fixed-radius,
   prepared-query, ranked-summary aggregate partials, not an RTNN-native
   shortcut.
2. Confirm whether the implementation separates summary aggregate output from
   ordered witness-row output.
3. Confirm whether the pod artifacts are valid: source commit
   `578cfe947037fff476c81b84a11e36ac6ac8fe45`, empty `source_dirty`, status
   pass, median timing, exact aggregate agreement with CuPy grid, and correct
   phase label for block-partial rows.
4. Confirm whether the timing table is accurate and bounded:
   - 32K uniform improves 1.146x but still trails CuPy at 0.920x.
   - 65K uniform improves 1.121x and crosses parity at 1.077x CuPy/RTDL.
   - 5 of 6 small rows now beat CuPy; only 32K uniform remains below parity.
   - 65K shell regresses modestly versus Goal2815 but still has a large 7.451x
     CuPy/RTDL margin.
5. Confirm whether the report keeps claim boundaries closed: no public
   RTDL-beats-CuPy claim, no RTDL-beats-RTNN-paper claim, no paper reproduction
   claim, no broad RT-core speedup claim, and no whole-app speedup claim.
6. Call out any stale wording, overclaim, missing evidence, artifact/test
   mismatch, determinism/concurrency risk, or app-agnosticity risk.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
Prefer `accept-with-boundary` unless you believe the public claim boundary can
be safely broadened without another independent review.
