# External Review Handoff: Goals4235-4236 Current-Head Rehearsal

Date: 2026-06-09

Please perform an independent read-only review of the Goal4235-4236 current-head
rehearsal chain.

## Files To Inspect

- `docs/reports/goal4235_current_head_rehearsal_after_measurement_closure_2026-06-09.md`
- `docs/reports/goal4235_current_head_rehearsal_rtx4000ada/current_scale_profile_packet.json`
- `docs/reports/goal4235_current_head_rehearsal_rtx4000ada/outputs/*.stdout.json`
- `docs/reports/goal4236_major_performance_target_map_after_current_head_rehearsal_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- `tests/goal4235_current_head_rehearsal_after_measurement_closure_test.py`
- `tests/goal4219_major_performance_target_map_test.py`

## Questions

1. Does Goal4235 legitimately prove that the current source head `72690687`
   executes all ten promoted benchmark front doors on RTX 4000 Ada with a clean
   pod worktree and 10/10 JSON-pass results?
2. Does the packet preserve the difference between current-head route health,
   measurement adequacy, and formal release/performance claims?
3. Does Goal4236 update the target map honestly by pointing current route health
   at Goal4235 while leaving release action, public speedup wording, paper
   reproduction wording, automatic partner selection, true-zero-copy wording,
   AMD/HIPRT evidence, and app-specific engine logic unauthorized?
4. Are the tests strong enough to catch stale commit provenance, failed rows,
   claim-boundary leakage, and route-policy drift?
5. What should be the next major target before any formal release packet?

## Required Output

Write one review file:

- Claude: `docs/reviews/goal4237_claude_review_goal4235_4236_current_head_rehearsal_2026-06-09.md`
- Gemini: `docs/reviews/goal4238_gemini_review_goal4235_4236_current_head_rehearsal_2026-06-09.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
State clearly that the review does not authorize release or public performance
claims unless you explicitly reject that boundary.
