# Goal906: Graph RT Documentation Sync After Goal905

Date: 2026-04-24

## Verdict

Updated stale graph RT-core planning and tutorial language after the Goal903-905
graph work. The public and planning docs no longer describe graph analytics as
only a host-indexed OptiX fallback.

## What Changed

- `docs/tutorials/graph_workloads.md` now explains:
  - default OptiX graph mode remains host-indexed and conservative
  - explicit `--optix-graph-mode native` exists for BFS and triangle-count
  - `--require-rt-core` is still rejected for BFS/triangle until the combined
    Goal889/905 RTX gate passes
- `docs/goal_823_v1_0_nvidia_rt_core_app_promotion_plan.md` now records graph
  as packaged but RTX-gated, not undecided.
- `scripts/goal848_v1_rt_core_goal_series.py` now describes Goal852 as RTX
  validation for graph native sub-paths rather than deciding whether graph
  should be removed from scope.
- `scripts/goal868_graph_redesign_decision_packet.py` now handles both states:
  old host-indexed-only fixtures and the current native-graph-ray-packaged state.

## Regenerated Artifacts

- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.json`
- `docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.md`
- `docs/reports/goal868_graph_redesign_decision_packet_2026-04-23.json`
- `docs/reports/goal868_graph_redesign_decision_packet_2026-04-23.md`

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal821_public_docs_require_rt_core_test tests.goal814_graph_optix_rt_core_honesty_gate_test tests.goal868_graph_redesign_decision_packet_test tests.goal848_v1_rt_core_goal_series_test tests.goal889_graph_visibility_optix_gate_test tests.goal903_embree_graph_ray_traversal_test -v
```

Result: `25` tests, `OK`.

```text
PYTHONPATH=src:. python3 -m py_compile scripts/goal868_graph_redesign_decision_packet.py scripts/goal848_v1_rt_core_goal_series.py examples/rtdl_graph_bfs.py examples/rtdl_graph_triangle_count.py examples/rtdl_graph_analytics_app.py tests/goal821_public_docs_require_rt_core_test.py tests/goal814_graph_optix_rt_core_honesty_gate_test.py tests/goal868_graph_redesign_decision_packet_test.py tests/goal903_embree_graph_ray_traversal_test.py
git diff --check
```

Result: both passed.

## Boundary

This is documentation and gate synchronization only. It does not authorize a
graph RTX claim. Graph promotion still requires a real RTX cloud artifact and
post-cloud review.
