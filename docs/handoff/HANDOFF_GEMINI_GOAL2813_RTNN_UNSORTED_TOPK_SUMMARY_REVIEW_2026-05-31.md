# Handoff: Gemini Review For Goal2813 RTNN Unsorted Top-K Summary Path

Please perform an independent read-only Gemini review of Goal2813 and write the
review to:

`docs/reviews/goal2813_gemini_review_rtnn_unsorted_topk_summary_2026-05-31.md`

## Context

Goal2813 follows Goal2812 in the v2.5 RTNN benchmark lane. Goal2812 made query
points device-resident for the fixed-radius 3D ranked-summary aggregate path.
Goal2813 then changes the float32 summary-only kernels to use an unsorted
bounded top-k helper instead of preserving sorted top-k order during traversal.

The intent is generic: when the output contract is only an aggregate summary,
the engine should not pay sorted row-output maintenance costs. This must remain
an app-agnostic fixed-radius ranked-summary optimization, not an RTNN-specific
native shortcut.

## Files To Inspect

- `docs/reports/goal2813_rtnn_unsorted_topk_summary_2026-05-31.md`
- `tests/goal2813_rtnn_unsorted_topk_summary_test.py`
- `src/native/optix/rtdl_optix_core.cpp`
- `docs/reports/goal2813_rtnn_unsorted_topk_summary_pod/rtnn_unsorted_topk_median_f32_32768.json`
- `docs/reports/goal2813_rtnn_unsorted_topk_summary_pod/rtnn_unsorted_topk_median_f32_65536.json`
- For comparison only:
  - `docs/reports/goal2812_rtnn_prepared_query_aggregate_2026-05-31.md`
  - `docs/reports/goal2812_rtnn_prepared_query_aggregate_pod/rtnn_prepared_query_median_f32_32768.json`
  - `docs/reports/goal2812_rtnn_prepared_query_aggregate_pod/rtnn_prepared_query_median_f32_65536.json`

## Review Questions

1. Confirm whether Goal2813 is a generic summary-only fixed-radius top-k
   optimization, not an RTNN-specific engine customization.
2. Confirm whether sorted row-output paths remain conceptually separate from the
   unsorted summary-only path.
3. Confirm whether the clean pod artifacts are valid: source commit
   `73270996cdeaff24cc7f90c7773818cccec73a8b`, empty `source_dirty`, status
   pass, median timing, `upload_sec: 0.0`, and exact aggregate agreement with
   the CuPy grid opponent.
4. Confirm whether the performance summary is accurate:
   - Goal2813 improves RTDL over Goal2812 by about 3.37x on 32K clustered,
     2.58x on 32K shell, 2.27x on 65K uniform, 3.19x on 65K clustered, and
     7.56x on 65K shell.
   - RTDL is faster than the CuPy grid opponent in 4 of 6 controlled rows
     (both clustered and both shell rows), but still slower on both uniform rows.
5. Confirm whether the report keeps claim boundaries closed: no public
   RTDL-beats-CuPy claim, no RTDL-beats-RTNN-paper claim, no paper reproduction
   claim, no broad RT-core claim, and no whole-app speedup claim.
6. Call out any stale wording, overclaim, missing evidence, artifact/test
   mismatch, determinism risk, or app-agnosticity risk.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
If accepted, prefer `accept-with-boundary` unless you believe the public claim
boundary can be safely broadened without another review.
