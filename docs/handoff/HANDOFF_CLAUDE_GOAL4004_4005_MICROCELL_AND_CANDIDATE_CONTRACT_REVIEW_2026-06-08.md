# Handoff: Claude Review Goal4004-4005 Microcell Rejection And Candidate Contract

Please perform a read-only review and write the result to:

`docs/reviews/goal4006_claude_review_goal4004_4005_microcell_and_candidate_contract_2026-06-08.md`

## Files To Inspect

- `docs/reports/goal4004_microcell_route_refresh_after_grouped_union_telemetry_2026-06-08.md`
- `docs/reports/goal4004_microcell_route_refresh_pod/*.json`
- `tests/goal4004_microcell_route_refresh_after_grouped_union_telemetry_test.py`
- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `docs/reports/goal4005_partition_convergence_candidate_front_door_contract_2026-06-08.md`
- `tests/goal4005_partition_convergence_candidate_front_door_contract_test.py`

## Questions

1. Does Goal4004 correctly reject the old corrected microcell route as a
   performance route while preserving it as a correctness lesson?
2. Does Goal4005 correctly expose `partition_convergence_hybrid` as a
   fail-closed candidate strategy rather than a supported runtime strategy?
3. Are all claim flags and hidden-dispatch/auto-partner flags closed?
4. Are the candidate requirements sufficient before native implementation:
   device-resident partition AABB/count columns, safe-full summary,
   ambiguous-boundary RT traversal, same-contract parity, deterministic roots,
   convergence/staleness counters, and actual-radius pod evidence?
5. What must the next native implementation goal guard against?

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
