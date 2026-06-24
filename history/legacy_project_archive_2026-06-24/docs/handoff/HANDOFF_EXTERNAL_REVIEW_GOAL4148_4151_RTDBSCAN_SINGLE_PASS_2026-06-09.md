# External Review Request - Goals4148-4151 RT-DBSCAN Single-Pass Direct-Status Candidate

Please review the RT-DBSCAN direct-status single-pass chain on current `main`.

## Scope

- Goal4148: `single_pass_candidate` convergence mode is exposed explicitly for
  the prepared direct-status component-signature path. Default remains
  `until_stable`.
- Goal4149: 1M/factor-0.25 pod comparison against the stable loop.
- Goal4150: 65k/131k/262k/524k factor-0.25 pod scale sweep.
- Goal4151: explicit advisor metadata surfaces the candidate as user-selected
  evidence, not hidden dispatch.

## Files To Inspect

- `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `docs/reports/goal4148_direct_status_single_pass_candidate_2026-06-09.md`
- `docs/reports/goal4149_direct_status_single_pass_candidate_pod_result_2026-06-09.md`
- `docs/reports/goal4150_direct_status_single_pass_scale_sweep_2026-06-09.md`
- `docs/reports/goal4151_rt_dbscan_single_pass_advisor_metadata_2026-06-09.md`
- `docs/reports/goal4149_direct_status_single_pass_1m_factor025_pod.json`
- `docs/reports/goal4150_direct_status_single_pass_scale_sweep_factor025_pod.json`
- `tests/goal4148_direct_status_single_pass_candidate_test.py`
- `tests/goal4149_direct_status_single_pass_candidate_pod_result_test.py`
- `tests/goal4150_direct_status_single_pass_scale_sweep_test.py`
- `tests/goal4151_rt_dbscan_single_pass_advisor_metadata_test.py`

## Questions

1. Does the implementation preserve the stable default and keep
   `single_pass_candidate` explicitly user-selected?
2. Are the pod results correctly interpreted: same signatures across measured
   profiles/scales, roughly 2x replay improvement, but no universal convergence
   proof because the final changed flag remains `1`?
3. Does Goal4151 expose useful advisor metadata without creating hidden
   dispatch, automatic partner/factor/convergence-mode selection, or public
   speedup/release claims?
4. Are there any correctness risks before using this candidate in more RT-DBSCAN
   benchmark timing packets?

## Required Output

Write a review to `docs/reviews/goal4152_<reviewer>_review_goal4148_4151_rtdbscan_single_pass_2026-06-09.md`.

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
Keep release/public-speedup/whole-app/RT-core/zero-copy/AMD claims blocked unless
you find separate evidence, which is not expected in this review.
