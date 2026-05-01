# Goal985 Graph Visibility Prepared Count

Date: 2026-04-26

Goal985 changes the graph app's OptiX `visibility_edges` summary path to use prepared ray/triangle any-hit count instead of materializing one row per candidate edge. It does not authorize public RTX speedup claims.

## Motivation

Goal982 rejected the current graph RTX speedup claim because the A5000 OptiX graph phase was slower than the same-scale Embree baseline. Goal984 removed avoidable graph cloud-gate chunking. Goal985 removes another avoidable cost in the graph visibility summary path: row materialization and row copyback.

The app summary only needs:

- `visible_edge_count`
- `blocked_edge_count`
- total candidate-edge row count

It does not need the individual `{"observer_id", "target_id", "visible"}` rows when `output_mode="summary"`.

## Change

For `examples/rtdl_graph_analytics_app.py`:

- `backend="optix"`, `scenario="visibility_edges"`, `output_mode="summary"` now builds visibility rays for the explicit candidate edges.
- It prepares blocker triangles with `rt.prepare_optix_ray_triangle_any_hit_2d(...)`.
- It prepares the ray batch with `rt.prepare_optix_rays_2d(...)`.
- It calls `prepared_scene.count(prepared_rays)` to get the blocked-edge count.
- It computes visible count as `candidate_edge_count - blocked_count`.
- It returns no materialized rows in summary mode.

The row-returning path is unchanged for non-summary usage. CPU/Embree/Vulkan/HIPRT compatibility paths continue to use `rt.visibility_pair_rows(...)`.

## Boundary

This is still a bounded graph visibility sub-path:

- It is not BFS acceleration.
- It is not triangle-count acceleration.
- It is not shortest-path, graph database, distributed graph analytics, or whole-app graph-system acceleration.
- It does not authorize public RTX speedup claims.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal889_graph_visibility_optix_gate_test
```

Result:

```text
Ran 16 tests in 0.461s
OK
```

The new test mocks the prepared OptiX scene and ray buffer, verifies that summary mode does not call `rt.visibility_pair_rows(...)`, verifies the `row_count` and visible/blocked counts, and checks the native continuation metadata.

## Next Cloud Action

The next RTX pod graph command should combine Goal984 and Goal985:

```text
python3 scripts/goal889_graph_visibility_optix_gate.py --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal889_graph_visibility_optix_gate_rtx.json
```

If the new artifact is still slower than the Goal982 Embree baseline, graph remains rejected for current public speedup claims. If it becomes competitive, it still needs separate claim-review packaging and 2-AI review before any public wording changes.
