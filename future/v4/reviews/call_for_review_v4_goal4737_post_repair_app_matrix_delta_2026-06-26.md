# Call For Review: V4 Goal4737 Post-Repair App Matrix Delta

Please review:

- `future/v4/v4_goal4737_post_repair_app_matrix_delta_2026-06-26.md`
- `future/v4/evidence/v4_goal4737_post_repair_app_matrix_delta_2026-06-26.json`
- `future/v4/evidence/v4_goal4732_raydb_device_output_route_repair_2026-06-26.json`
- `future/v4/evidence/v4_goal4733_triangle_v3_regression_resolution_2026-06-26.json`
- `future/v4/evidence/v4_goal4734_rt_dbscan_generic_continuation_no_go_2026-06-26.json`
- `future/v4/evidence/v4_goal4736_barnes_hut_complete_workflow_focused_pod_2026-06-26.json`
- `tests/v4_goal4737_post_repair_matrix_delta_test.py`

## Context

Goal4730 froze the complete 10-app matrix and blocked formal high-performance
V4. Goals4732-4736 moved several rows. Goal4737 records the delta without
rewriting Goal4730 history.

Current internal candidate rows:

- `hausdorff_xhd`
- `triangle_counting`
- `barnes_hut`

Formal release remains blocked because RayDB still regresses versus V3, and
several apps remain parity/no-win/no-go/no-route.

## Questions For Reviewer

1. Is it correct to preserve Goal4730 as historical frozen matrix and record
   Goal4737 as a delta?
2. Are the three candidate rows correctly counted?
3. Is RayDB correctly kept as a remaining blocker due V4/V3 `0.954x`?
4. Is Barnes-Hut wording bounded correctly as V2.14 candidate win and V3
   no-regression, not RT-core force-law speedup?
5. Is the formal tag still correctly blocked?
6. Are the next goals ordered correctly?

## Requested Verdict Labels

- `accept_goal4737_delta_matrix_improved_but_blocked`
- `accept_with_required_amendments`
- `reject_goal4737_overcounts_or_overclaims`

## Non-Authorization

This review must not authorize final V4 tag, public all-benchmark speed claims,
geomean headlines, broad V4-over-V3 wording, arbitrary callbacks,
app-specific native kernels, true-zero-copy wording, or hiding remaining
blockers.
