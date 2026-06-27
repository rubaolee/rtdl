# Call For Review: V4 Goal4735 Fresh Generic Operator Target Selection

Please review:

- `future/v4/v4_goal4735_fresh_generic_operator_target_selection_2026-06-26.md`
- `future/v4/evidence/v4_goal4735_fresh_generic_operator_target_selection_2026-06-26.json`
- `future/v4/v4_goal4728_spatial_rayjoin_no_route_blocker_row_2026-06-26.md`
- `future/v4/v4_goal4729_barnes_hut_deferred_subprobe_row_2026-06-26.md`
- `scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py`
- `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `tests/v4_goal4735_fresh_operator_target_selection_test.py`

## Context

Goal4735 chooses the next fresh generic-operator target after:

- Goal4732 repaired RayDB route binding;
- Goal4733 cleared triangle V4/V3 regression;
- Goal4734 closed RTDBSCAN as no-go.

The selected target is Barnes-Hut, not Spatial RayJoin.

## Questions For Reviewer

1. Is Barnes-Hut the correct next target, given current route readiness and the
   existing complete aggregate-frontier plus weighted-vector workflow frontdoor?
2. Is Spatial RayJoin correctly rejected for now because it has no complete V4
   app route and the shape-pair subprobe failed speed-credit bars?
3. Are the Goal4736 gates strict enough to prevent subprobe evidence from being
   misread as a whole-app win?
4. Does the selected Barnes-Hut route remain generic if it uses aggregate
   frontier device columns plus explicit partner weighted-vector continuation,
   without a Barnes-Hut identity native kernel?
5. Are the non-authorization boundaries sufficient?

## Requested Verdict Labels

- `accept_goal4735_select_barnes_hut_for_goal4736`
- `accept_with_required_amendments`
- `reject_goal4735_target_selection`

## Non-Authorization

This review must not authorize final V4 tag, public speed claims, Barnes-Hut
speedup claims, all-benchmark speedups, geomean headlines, arbitrary callbacks,
app-specific native kernels, true-zero-copy wording, or treating Goal4735 target
selection as Goal4736 measurement success.
