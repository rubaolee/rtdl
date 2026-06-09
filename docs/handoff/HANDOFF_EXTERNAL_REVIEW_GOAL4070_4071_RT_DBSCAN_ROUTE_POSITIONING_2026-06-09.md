# External Review Handoff: Goals4070-4071 RT-DBSCAN Route Positioning

Date: 2026-06-09

Please perform an independent read-only review of Goals4070-4071 on current
`main`.

## Scope

Review these deliverables:

- `docs/reports/goal4070_rt_dbscan_partition_pair_enumeration_app_timing_2026-06-09.md`
- `docs/reports/goal4070_rt_dbscan_partition_pair_enumeration_app_timing_pod.json`
- `docs/reports/goal4070_rt_dbscan_partition_pair_enumeration_app_timing_pod.stdout.txt`
- `docs/reports/goal4071_rt_dbscan_current_recommended_route_after_partition_2026-06-09.md`
- `docs/reports/goal4071_rt_dbscan_current_recommended_route_after_partition_pod.json`
- `docs/reports/goal4071_rt_dbscan_current_recommended_route_after_partition_pod.stdout.txt`
- `scripts/goal4070_rt_dbscan_partition_pair_enumeration_app_timing.py`
- `scripts/goal4071_rt_dbscan_current_recommended_route_after_partition.py`
- `tests/goal4070_rt_dbscan_partition_pair_enumeration_app_timing_test.py`
- `tests/goal4071_rt_dbscan_current_recommended_route_after_partition_test.py`

## Questions

1. Does Goal4070 correctly conclude that `device_count_then_emit` is an
   explicit memory-pressure option (13.13x-209.35x capacity reduction in the
   pod packet) but not a default app-level performance win?
2. Does Goal4071 correctly compare normalized component-size signatures rather
   than incorrectly treating different app-level signature schemas as a
   correctness mismatch?
3. Does the current route-positioning evidence support keeping the RT-core
   grouped-stream Numba signature route as the recommended RT-DBSCAN route after
   the partition-preview chain?
4. Are all claim boundaries closed: no release authorization, no public speedup
   wording, no broad RT-core speedup wording, no whole-app benchmark claim, no
   paper-reproduction claim, no hidden dispatch, no automatic partner selection,
   no app-specific native engine logic, no native ABI addition, and no
   true-zero-copy claim?
5. What should be the next engineering target if we want a real performance
   improvement rather than more partition-preview timing?

## Expected Output

Write exactly one review file:

- Claude: `docs/reviews/goal4072_claude_review_goal4070_4071_rt_dbscan_route_positioning_2026-06-09.md`
- Gemini: `docs/reviews/goal4073_gemini_review_goal4070_4071_rt_dbscan_route_positioning_2026-06-09.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This review must be independent from Codex authoring. Codex+Codex is invalid
consensus.
