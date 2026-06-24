# External Review Handoff - Goals 4116-4118 RT-DBSCAN Tuned Direct Status

Date: 2026-06-09

## Requested Review

Please perform a read-only external review of the Goal4116-4118 RT-DBSCAN chain.

Expected outputs:

- Claude: `docs/reviews/goal4119_claude_review_goal4116_4118_tuned_direct_status_2026-06-09.md`
- Gemini: `docs/reviews/goal4120_gemini_review_goal4116_4118_tuned_direct_status_2026-06-09.md`

Use verdict values only from: `accept`, `accept-with-boundary`, `reject`, `needs-more-evidence`.

## Scope

Review these deliverables:

- Goal4116 app-surface change:
  - `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
  - `tests/goal4116_rt_dbscan_explicit_partition_cell_factor_test.py`
- Goal4117 timing runner/evidence:
  - `scripts/goal4117_partition_cell_factor_route_sweep.py`
  - `docs/reports/goal4117_partition_cell_factor_route_sweep_2026-06-09.md`
  - `docs/reports/goal4117_partition_cell_factor_route_sweep_pod.json`
  - `tests/goal4117_partition_cell_factor_route_sweep_test.py`
- Goal4118 route refresh:
  - `src/rtdsl/current_benchmark_route_decisions.py`
  - `docs/reports/goal4118_current_route_decision_after_tuned_direct_status_2026-06-09.md`
  - `tests/goal4118_current_route_decision_after_tuned_direct_status_test.py`
- Relevant prior context:
  - `docs/reports/goal4114_prepared_direct_status_app_repeat_route_timing_2026-06-09.md`
  - `docs/reports/goal4115_current_route_decision_after_shape_dependent_direct_status_2026-06-09.md`
  - `docs/reviews/goal4111_claude_review_goal4107_4110_prepared_direct_status_chain_2026-06-09.md`
  - `docs/reviews/goal4112_gemini_review_goal4107_4110_prepared_direct_status_chain_2026-06-09.md`

## Questions To Answer

1. Does Goal4116 expose `partition_cell_factor` as an explicit user-selected control, without hidden dispatch or automatic tuning?
2. Does Goal4117 fairly compare the explicit prepared direct-status route against the current grouped-stream Numba route for the same repeated component-signature contract?
3. Are the key Goal4117 measured results correctly stated?
   - `clustered3d`: factor `0.25`, replay speedup `2.961x`
   - `road3d`: factor `0.25`, replay speedup `1.866x`
   - `ngsim_dense`: factor `0.5`, replay speedup `1.312x`
4. Does the `ngsim_dense` interpretation hold: the Goal4114 loss was caused by the tested default partition granularity, and the larger explicit factor repairs it while preserving signature equality?
5. Does Goal4118 correctly change RT-DBSCAN route guidance to `mixed_explicit_user_choice` without authorizing automatic factor selection or universal default promotion?
6. Are all claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper-reproduction, true-zero-copy, hidden-dispatch, automatic partner selection, automatic factor selection, native ABI, app-specific engine logic, or AMD performance claims?
7. Are there correctness, determinism, app-agnostic, or performance-risk issues that should block the next engineering step?

## Required Boundary

Do not edit source code. A review file may be written to the expected output path. Do not authorize release or public claims. Treat this as internal route-guidance and benchmark-development evidence only.
