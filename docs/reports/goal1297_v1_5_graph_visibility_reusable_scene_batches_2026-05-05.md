# Goal1297: Graph Visibility Reusable Prepared Scene Batches

Date: 2026-05-05

## Purpose

Goal1297 moves the graph `visibility_edges` OptiX summary diagnostic one step
toward the v1.5 architecture: the app can split graph-edge rays into multiple
batches while reusing one app-name-free generic prepared ray/triangle scene.

This is an internal v1.5 engineering slice, not public speedup wording.

## Change

- Added `--visibility-ray-batches N` to
  `examples/rtdl_graph_analytics_app.py`.
- The option is valid only for:
  `--backend optix --scenario visibility_edges --output-mode summary`.
- The default remains `1`, preserving the existing
  `run_prepared_visibility_anyhit_count` compatibility wrapper path.
- When `N > 1`, the graph app:
  - packs the blocker triangle scene once;
  - opens `prepare_generic_ray_triangle_any_hit_scene(...)` once;
  - packs each ray batch independently;
  - calls `GenericPreparedRayTriangleAnyHitScene.count(...)` for each batch;
  - reports aggregate visible/blocked counts, aggregate timing phases, and
    per-batch summaries.

## Boundary

This remains the bounded graph visibility sub-path only. It does not accelerate
BFS, triangle counting, shortest path, graph databases, frontier bookkeeping, or
general graph reductions.

## Local Verification

Passed locally:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1297_v1_5_graph_visibility_reusable_scene_batches_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal1295_v1_5_generic_prepared_scene_session_test \
  tests.goal1296_v1_5_prepared_scene_session_evidence_test
```

Result: 22 tests OK.

Passed locally:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_graph_analytics_app.py \
  tests/goal1297_v1_5_graph_visibility_reusable_scene_batches_test.py
```

## Next Pod Action

Run the graph OptiX summary path on the active pod with a large copy count and
multiple ray batches, then copy back:

```text
docs/reports/goal1297_v1_5_graph_visibility_reusable_scene_batches_pod_results/
```
