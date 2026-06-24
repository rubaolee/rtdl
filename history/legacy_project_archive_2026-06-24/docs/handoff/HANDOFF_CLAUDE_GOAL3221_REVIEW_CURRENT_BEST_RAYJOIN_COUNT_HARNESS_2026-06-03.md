# Handoff: Goal3221 Claude Review of Goal3220 Current-Best RayJoin Count Harness

Please perform a read-only independent Claude review of Goal3220, the current-best
Spatial RayJoin count/parity harness.

## Expected Output

Write the review to:

`docs/reviews/goal3221_claude_review_goal3220_current_best_rayjoin_count_harness_2026-06-03.md`

Use one of the accepted verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

## Files to Inspect

- `scripts/goal3220_spatial_rayjoin_current_best_count_harness.py`
- `docs/reports/goal3220_spatial_rayjoin_current_best_count_harness_2026-06-03.md`
- `docs/reports/goal3220_spatial_rayjoin_current_best_count_harness_2026-06-03.json`
- `docs/reports/goal3220_spatial_rayjoin_current_best_count_harness_2026-06-03.stdout`
- `tests/goal3220_spatial_rayjoin_current_best_count_harness_test.py`
- `tests/goal3220_spatial_rayjoin_current_best_count_harness_artifact_test.py`
- Relevant prior review context:
  - `docs/reviews/goal3214_claude_review_fused_segment_pair_count_chain_2026-06-03.md`
  - `docs/reviews/goal3217_gemini_review_post_claude_fused_count_hardening_2026-06-03.md`
  - `docs/reviews/goal3219_claude_review_goal3218_rayjoin_public_lsi_dense_probe_2026-06-03.md`

## Review Questions

1. Does Goal3220 correctly define a current-best internal Spatial RayJoin
   count/parity harness without rewriting or overloading historical Goal2799?
2. Does the route policy make sense: PIP uses the existing prepared OptiX count
   route, LSI uses the new fused dense left-id count route, and overlay-seed uses
   the existing prepared OptiX count route?
3. Does the harness preserve the app-agnostic native boundary, with RayJoin
   interpretation kept in Python and generic contracts passed to native OptiX?
4. Does the pod evidence prove only count/parity correctness on the current
   fixture rows, and avoid overclaiming row overlay continuation, release
   readiness, public speedup, true zero-copy, or RayJoin paper reproduction?
5. Are the hardware metadata, commit provenance, test assertions, and
   claim-boundary flags sufficient for internal v2.8/v3.0 planning evidence?
6. What remains before this harness can support stronger RayJoin benchmark
   claims or paper-level comparison?

## Boundaries

This is a read-only review. Do not edit source files, reports, artifacts, or
tests other than writing the requested review file.

The review must not authorize release, public speedup claims, broad RT-core
claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin paper
reproduction claims unless the evidence unexpectedly and explicitly proves them.
The expected position is that Goal3220 is an internal current-best harness,
count/parity-only, with row overlay continuation still deferred.
