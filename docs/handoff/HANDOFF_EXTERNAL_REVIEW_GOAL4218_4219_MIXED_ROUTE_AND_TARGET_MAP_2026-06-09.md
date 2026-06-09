# External Review Request: Goals4218-4219 Mixed-Route Evidence And Major Target Map

Please perform an independent review of Goals4218-4219.

## Files To Inspect

- `docs/reports/goal4218_mixed_route_focus_after_policy_2026-06-09.md`
- `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/summary_manifest.json`
- `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/rayjoin/summary.json`
- `docs/reports/goal4218_mixed_route_focus_after_policy_rtx4000ada/rtdbscan/*.json`
- `tests/goal4218_mixed_route_focus_after_policy_test.py`
- `src/rtdsl/current_major_performance_targets.py`
- `docs/reports/goal4219_major_performance_target_map_after_goal4218_2026-06-09.md`
- `tests/goal4219_major_performance_target_map_test.py`

## Review Questions

1. Does Goal4218 correctly present the RayJoin result as contract-split route evidence rather than whole-app RayJoin or paper-reproduction evidence?
2. Does Goal4218 correctly show that, for the current 65k clustered3d RT-DBSCAN profile, unblocked canonical single-pass grouped stream is preferable to the blocked grouped-stream variant?
3. Does Goal4219 keep the next performance direction at the generic language/runtime level rather than app-only micro-tuning?
4. Does Goal4219 preserve explicit user partner choice and avoid automatic partner/backend dispatch?
5. Do all claim boundaries remain closed: no release, public speedup, whole-app acceleration, broad RT-core, paper reproduction, true-zero-copy, AMD performance, or app-specific native-engine claim?

## Expected Output

Write your review to:

- Claude: `docs/reviews/goal4220_claude_review_goal4218_4219_mixed_route_target_map_2026-06-09.md`
- Gemini: `docs/reviews/goal4221_gemini_review_goal4218_4219_mixed_route_target_map_2026-06-09.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
