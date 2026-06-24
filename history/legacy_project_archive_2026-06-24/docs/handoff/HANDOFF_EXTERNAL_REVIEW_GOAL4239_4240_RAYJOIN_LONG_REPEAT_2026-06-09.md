# External Review Handoff: Goals4239-4240 RayJoin Long-Repeat

Date: 2026-06-09

Please perform an independent read-only review of the Goal4239-4240 RayJoin
long-repeat evidence chain.

## Files To Inspect

- `docs/reports/goal4239_rayjoin_dedicated_long_repeat_profile_2026-06-09.md`
- `docs/reports/goal4239_rayjoin_dedicated_long_repeat_rtx4000ada/rayjoin_long_repeat.stdout.json`
- `docs/reports/goal4239_rayjoin_dedicated_long_repeat_rtx4000ada/rayjoin_long_repeat.stderr.txt`
- `docs/reports/goal4240_major_performance_target_map_after_rayjoin_long_repeat_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- `tests/goal4239_rayjoin_dedicated_long_repeat_profile_test.py`
- `tests/goal4219_major_performance_target_map_test.py`

## Questions

1. Does Goal4239 legitimately close the earlier RayJoin dedicated long-repeat
   evidence gap with a clean-source, 20+ second representative mixed-route run?
2. Does the report preserve the contract split: Numba for bounded PIP one-shot,
   prepared RTDL/OptiX for repeated PIP, LSI scalar count, and overlay active
   count?
3. Does Goal4240 update the major performance target map honestly by citing
   Goal4239 without authorizing release action, public speedup wording,
   RayJoin paper-reproduction wording, RTDL-beats-RayJoin wording, automatic
   partner selection, true-zero-copy wording, AMD performance wording, or
   app-specific native-engine logic?
4. Are the tests sufficient to catch route collapse, claim-boundary leakage, and
   stale provenance?
5. What should be the next major target before any formal release packet?

## Required Output

Write one review file:

- Claude: `docs/reviews/goal4241_claude_review_goal4239_4240_rayjoin_long_repeat_2026-06-09.md`
- Gemini: `docs/reviews/goal4242_gemini_review_goal4239_4240_rayjoin_long_repeat_2026-06-09.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
State explicitly whether the evidence remains internal-only.
