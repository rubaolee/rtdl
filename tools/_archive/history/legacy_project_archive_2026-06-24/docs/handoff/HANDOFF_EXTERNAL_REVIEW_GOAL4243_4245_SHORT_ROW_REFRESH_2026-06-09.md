# External Review Handoff: Goals4243-4245 Short-Row Refresh

Date: 2026-06-09

Please perform an independent read-only review of the Goal4243-4245 evidence
and hardening chain.

## Files To Inspect

- `docs/reports/goal4243_short_row_long_repeat_refresh_2026-06-09.md`
- `docs/reports/goal4243_short_row_long_repeat_refresh_rtx4000ada/summary.json`
- `docs/reports/goal4243_short_row_long_repeat_refresh_rtx4000ada/*.stdout.json`
- `docs/reports/goal4244_major_performance_target_map_after_short_row_refresh_2026-06-09.md`
- `docs/reports/goal4245_rayjoin_review_gap_hardening_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- `tests/goal4243_short_row_long_repeat_refresh_test.py`
- `tests/goal4239_rayjoin_dedicated_long_repeat_profile_test.py`
- `tests/goal4219_major_performance_target_map_test.py`

## Questions

1. Does Goal4243 legitimately refresh the former current-head short rows
   (Hausdorff, contact manifold, triangle counting) with dedicated repeat
   evidence at clean source commit `9a40f7f5`?
2. Do the three rows preserve their scoped meanings and avoid overclaiming
   exact Hausdorff, full physics, or paper-system reproduction?
3. Does Goal4244 update the target map honestly without authorizing release or
   public claims?
4. Does Goal4245 correctly resolve the two minor Goal4241 findings:
   `wrapper_elapsed_sec > 20.0` for RayJoin and structural
   `rtdl_beats_rayjoin_claim_authorized` guard in the target-map dataclass?
5. What remains before a formal release packet?

## Required Output

Write one review file:

- Claude: `docs/reviews/goal4246_claude_review_goal4243_4245_short_row_refresh_2026-06-09.md`
- Gemini: `docs/reviews/goal4247_gemini_review_goal4243_4245_short_row_refresh_2026-06-09.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
State explicitly whether this evidence remains internal-only.
