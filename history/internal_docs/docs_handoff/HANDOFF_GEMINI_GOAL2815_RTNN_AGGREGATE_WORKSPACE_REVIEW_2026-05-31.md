# Handoff: Gemini Review For Goal2815 RTNN Prepared Aggregate Workspace

Please perform an independent read-only Gemini review of Goal2815 and write the
review to:

`docs/reviews/goal2815_gemini_review_rtnn_prepared_aggregate_workspace_2026-05-31.md`

## Context

Goal2815 follows Goal2813 and Goal2814 in the v2.5 RTNN lane. Goal2813 added
the unsorted summary-only bounded top-k path. Goal2814 showed that the path wins
at larger scales, while small 32K/65K uniform rows still have fixed overhead.
Goal2815 implements a generic small runtime improvement: the prepared fixed-
radius search handle now owns a reusable aggregate device workspace instead of
allocating the tiny aggregate buffer on every aggregate call.

This must be reviewed as a generic fixed-radius ranked-summary runtime
improvement, not an RTNN-specific native customization.

## Files To Inspect

- `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_2026-05-31.md`
- `tests/goal2815_rtnn_prepared_aggregate_workspace_test.py`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_pod/rtnn_workspace_baseline_median_f32_32768.json`
- `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_pod/rtnn_workspace_baseline_median_f32_65536.json`
- `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_pod/rtnn_workspace_median_f32_32768.json`
- `docs/reports/goal2815_rtnn_prepared_aggregate_workspace_pod/rtnn_workspace_median_f32_65536.json`

## Review Questions

1. Confirm whether the implementation is generic: a prepared fixed-radius
   ranked-summary aggregate workspace, not an RTNN-specific native path.
2. Confirm whether the workspace lifetime is reasonable for the current
   synchronous prepared-handle contract: allocate in prepared search handle,
   clear per aggregate call, reuse for prepared-query and non-resident-query
   aggregate paths, destroy with the prepared handle.
3. Confirm whether the A/B evidence is valid:
   - Pre-workspace commit `8dacc429105d33f1e08bb43fef4c843d266bba75`
   - Post-workspace commit `95218cf43094ee3fdc2826c4f5ea07cb175bbeb4`
   - Clean `source_dirty: []`
   - Repeat 5 median timing
   - Exact aggregate agreement with CuPy grid
4. Confirm whether the timing table is accurate and bounded:
   - 32K uniform improves 1.143x but still trails CuPy at 0.797x.
   - 65K uniform improves 1.127x but still trails CuPy at 0.885x.
   - The clustered/shell rows improve modestly and still beat CuPy.
5. Confirm whether the report avoids overclaiming: no public RTDL-beats-CuPy
   claim, no RTDL-beats-RTNN-paper claim, no paper reproduction claim, no broad
   RT-core speedup claim, and no whole-app speedup claim.
6. Call out any stale wording, overclaim, missing evidence, artifact/test
   mismatch, determinism/concurrency risk, or app-agnosticity risk.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
Prefer `accept-with-boundary` unless you believe the public claim boundary can
be safely broadened without another review.
