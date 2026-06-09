# External Review Handoff - Goals4107-4110 RT-DBSCAN Prepared Direct Status Chain

Please perform a read-only external review of Goals4107-4110 on current `main`.

## Scope

Review these commits and artifacts:

- Goal4107: prepared direct-status union handle
  - `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`
  - `src/rtdsl/__init__.py`
  - `tests/goal4107_prepared_direct_status_union_handle_test.py`
- Goal4108: prepared direct-status reuse timing
  - `scripts/goal4108_prepared_direct_status_reuse_timing.py`
  - `docs/reports/goal4108_prepared_direct_status_reuse_timing_2026-06-09.md`
  - `docs/reports/goal4108_prepared_direct_status_reuse_timing_pod.json`
  - `tests/goal4108_prepared_direct_status_reuse_timing_test.py`
- Goal4109: explicit RT-DBSCAN app mode
  - `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
  - `docs/reports/goal4109_rt_dbscan_prepared_direct_status_app_mode_2026-06-09.md`
  - `docs/reports/goal4109_prepared_direct_status_app_mode_tiny_pod.json`
  - `docs/reports/goal4109_prepared_direct_status_app_mode_clustered65536_pod.json`
  - `tests/goal4109_rt_dbscan_prepared_direct_status_app_mode_test.py`
- Goal4110: current route guidance refresh
  - `src/rtdsl/current_benchmark_route_decisions.py`
  - `docs/reports/goal4110_current_route_decision_after_prepared_direct_status_app_mode_2026-06-09.md`
  - `tests/goal4110_current_route_decision_after_prepared_direct_status_app_mode_test.py`

## Questions

1. Does Goal4107 genuinely prepare reusable point/partition columns without materializing near-pair columns or app-specific native ABI?
2. Does Goal4108 fairly distinguish prepared replay evidence from one-shot/default-route evidence?
3. Does Goal4109 expose a clear user-facing app mode while preserving the graph-component-only and non-default-route boundary?
4. Does Goal4110 correctly keep one-shot RT-DBSCAN guidance conservative while allowing explicit prepared direct-status use for repeated component-signature workloads?
5. Are claim boundaries intact: no release, public speedup, broad RT-core, whole-app, paper-reproduction, true-zero-copy, hidden-dispatch, automatic-partner-selection, native-ABI, or app-specific-engine claims?
6. Are there correctness, determinism, route-guidance, or performance-risk issues that should block the next engineering step?

## Required Output

Write a review file with verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Suggested Claude output path:

`docs/reviews/goal4111_claude_review_goal4107_4110_prepared_direct_status_chain_2026-06-09.md`

Suggested Gemini output path:

`docs/reviews/goal4112_gemini_review_goal4107_4110_prepared_direct_status_chain_2026-06-09.md`

Do not edit source files. If you run tests, record exact commands and results.
