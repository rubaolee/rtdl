# Call For Review: V4 Goal4736 Barnes-Hut Complete Workflow Focused POD

Please review:

- `future/v4/v4_goal4736_barnes_hut_complete_workflow_focused_pod_2026-06-26.md`
- `future/v4/evidence/v4_goal4736_barnes_hut_complete_workflow_focused_pod_2026-06-26.json`
- `future/v4/evidence/v4_goal4735_barnes_hut_focused_20260626/summary.json`
- `future/v4/evidence/v4_goal4735_barnes_hut_focused_20260626/v2_14_serious.json`
- `future/v4/evidence/v4_goal4735_barnes_hut_focused_20260626/v3_0_2_serious.json`
- `future/v4/evidence/v4_goal4735_barnes_hut_focused_20260626/v4_current_serious.json`
- `future/v4/evidence/v4_goal4735_barnes_hut_focused_20260626/v4_current_correctness.json`
- `scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py`
- `tests/v4_goal4736_barnes_hut_complete_workflow_test.py`

## Context

Goal4735 froze Barnes-Hut gates before measurement. Goal4736 ran the complete
aggregate-frontier plus weighted-vector workflow on the same RT-hardware POD.

Focused result:

- V4/V2.14 full hot: `282.46785456124815`
- V4/V2.14 full wall: `204.69570811814097`
- V4/V3.0.2 full hot: `1.00274877675932`
- correctness companion: pass
- V4 host frontier materialization in hot path: false
- partner migration counted as speed: false

## Questions For Reviewer

1. Does Goal4736 validly move Barnes-Hut from deferred/subprobe to a complete
   app-level candidate row?
2. Is the result correctly classified as strong V4/V2.14 improvement plus V3
   no-regression, not broad V4/V3 speedup?
3. Does the route remain generic runtime/operator work rather than a
   Barnes-Hut-identity native kernel?
4. Is it correct to forbid RT-core force-law speedup wording for this row?
5. Is the old Goal4729 deferred row properly superseded rather than erased?
6. Are the non-authorization boundaries sufficient?

## Requested Verdict Labels

- `accept_goal4736_barnes_hut_complete_candidate_row`
- `accept_with_required_amendments`
- `reject_goal4736_not_complete_or_overclaimed`

## Non-Authorization

This review must not authorize final V4 tag, public all-benchmark speed claims,
RT-core force-law claims, native Barnes-Hut kernel claims, broad V4-over-V3
speedup wording, arbitrary callbacks, app-specific native kernels,
true-zero-copy wording, or hiding the old deferred/subprobe row.
