# Handoff: Gemini Review For Goal2814 RTNN Scale Sweep

Please perform an independent read-only Gemini review of Goal2814 and write the
review to:

`docs/reviews/goal2814_gemini_review_rtnn_unsorted_topk_scale_sweep_2026-05-31.md`

## Context

Goal2814 records a larger same-contract RTNN scale sweep for the Goal2813
unsorted bounded top-k summary path. Goal2813 showed RTDL faster than the CuPy
grid opponent in 4 of 6 controlled 32K/65K rows, while both uniform rows were
still slower. Goal2814 asks whether the uniform weakness is a primitive design
problem or small-row overhead.

No source code changes were made for Goal2814. It is an evidence/report/test
goal over the already-implemented Goal2813 path.

## Files To Inspect

- `docs/reports/goal2814_rtnn_unsorted_topk_scale_sweep_2026-05-31.md`
- `tests/goal2814_rtnn_unsorted_topk_scale_sweep_test.py`
- `docs/reports/goal2814_rtnn_unsorted_topk_scale_sweep_pod/rtnn_unsorted_topk_scale_131072.json`
- `docs/reports/goal2814_rtnn_unsorted_topk_scale_sweep_pod/rtnn_unsorted_topk_scale_262144.json`
- Context:
  - `docs/reports/goal2813_rtnn_unsorted_topk_summary_2026-05-31.md`
  - `docs/reviews/goal2813_gemini_review_rtnn_unsorted_topk_summary_2026-05-31.md`

## Review Questions

1. Confirm whether Goal2814 is correctly scoped as scale evidence only, not a
   new implementation goal.
2. Confirm whether the artifacts are valid: source commit
   `8db92cafaf8b054dcaed67a40b9fa6ca31828066`, empty `source_dirty`, status
   pass, median timing, query-resident `upload_sec: 0.0`, and exact aggregate
   agreement with the CuPy grid opponent.
3. Confirm whether the timing table is accurate:
   - 131072 uniform: 0.000302740 RTDL vs 0.000576740 CuPy, 1.905x
   - 131072 clustered: 0.067074863 RTDL vs 0.150910448 CuPy, 2.250x
   - 131072 shell: 0.002534534 RTDL vs 0.028577222 CuPy, 11.275x
   - 262144 uniform: 0.000965423 RTDL vs 0.003626705 CuPy, 3.757x
   - 262144 clustered: 0.224376351 RTDL vs 0.439262436 CuPy, 1.958x
   - 262144 shell: 0.033773679 RTDL vs 0.144271217 CuPy, 4.272x
4. Confirm whether the interpretation is fair: the earlier small uniform rows
   were likely limited by fixed small-row overhead, while the generic primitive
   scales well at larger row counts.
5. Confirm whether claim boundaries remain closed: no public RTDL-beats-CuPy
   claim, no RTDL-beats-RTNN-paper claim, no paper reproduction claim, no broad
   RT-core speedup claim, and no whole-app speedup claim.
6. Call out any stale wording, overclaim, missing evidence, artifact/test
   mismatch, or app-agnosticity risk.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
Prefer `accept-with-boundary` unless you believe the evidence safely justifies a
broader public claim without another review.
