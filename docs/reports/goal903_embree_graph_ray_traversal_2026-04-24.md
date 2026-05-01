# Goal903: Embree Graph Ray Traversal for BFS and Triangle Count

Date: 2026-04-24

## Verdict

Implemented local Embree graph-ray candidate generation for the graph BFS and
triangle-count examples. This closes the previous local gap where graph BFS and
triangle-count were Embree BVH-assisted through `rtcPointQuery`, but not actual
ray traversal.

This is not yet a NVIDIA RT-core claim. OptiX BFS and triangle-count still need
their own graph-ray lowering and RTX cloud artifact.

## Problem

The graph app had three sub-paths:

- `visibility_edges`: mapped graph-like candidate edges to ray/triangle any-hit.
- `bfs`: emitted discovered graph edges from a CSR frontier expansion.
- `triangle_count`: emitted triangles by probing common neighbors of seed edges.

Before this goal, Embree BFS and triangle-count built Embree user geometry over
CSR edge points and used `rtcPointQuery` to collect neighbors. That was useful
BVH-assisted candidate lookup, but it did not satisfy the stricter project goal
that application candidate generation should be implemented as RT traversal
where a paper-style RT mapping exists.

## Implementation

The Embree native graph path now represents each directed CSR edge as a small
user-geometry primitive at `(src_vertex, 0)`, with `dst_vertex` stored as the
primitive payload. Querying a source vertex shoots a vertical ray from
`(src_vertex, -1)` through that source column. This is a source-column ray
formulation for outgoing-edge candidate generation; it does not spatially encode
destination IDs on the y-axis.

For BFS:

- one ray is issued per frontier vertex
- ray hits collect outgoing candidate edges
- visited and dedupe filtering remain CPU-side because they are graph-state
  bookkeeping, not traversal
- emitted rows remain `src_vertex`, `dst_vertex`, `level`

For triangle count:

- one ray is issued for `u` and one for `v` for each seed edge `(u, v)`
- the hit callback collects each endpoint's neighbor set
- CPU-side set intersection and uniqueness filtering produce `(u, v, w)` rows
- emitted rows and deterministic ordering remain unchanged

## Files Changed

- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`
- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`
- `examples/rtdl_graph_analytics_app.py`
- `src/rtdsl/app_support_matrix.py`
- `docs/app_engine_support_matrix.md`
- `docs/reports/goal902_app_by_app_rt_usage_and_next_moves_2026-04-24.md`
- `tests/goal903_embree_graph_ray_traversal_test.py`

## Honesty Boundary

This goal upgrades Embree graph BFS and triangle-count from point-query BVH
assistance to ray traversal over graph-edge primitives. It does not claim:

- full BFS over all levels
- shortest paths
- distributed graph analytics
- whole graph database acceleration
- NVIDIA RT-core acceleration for BFS or triangle-count

The current NVIDIA graph claim remains bounded to `visibility_edges` until an
OptiX graph-ray lowering exists and passes cloud validation.

## Verification

Executed locally:

```text
make build-embree
PYTHONPATH=src:. python3 -m unittest tests.goal396_v0_6_rt_graph_triangle_embree_test tests.goal395_v0_6_rt_graph_bfs_vulkan_test -v
PYTHONPATH=src:. python3 -m unittest tests.goal903_embree_graph_ray_traversal_test -v
PYTHONPATH=src:. python3 -m py_compile examples/rtdl_graph_bfs.py examples/rtdl_graph_triangle_count.py examples/rtdl_graph_analytics_app.py tests/goal903_embree_graph_ray_traversal_test.py src/rtdsl/app_support_matrix.py
git diff --check
```

Results:

- Embree build check completed with Embree `4.4.0`.
- Existing focused graph test suite: `9` tests, `OK`, `4` skips for unavailable Vulkan.
- New Goal903 suite: `4` tests, `OK`.
- `py_compile`: OK.
- `git diff --check`: OK.

## Next Move

Use this Embree graph-ray path as the local correctness prototype for the
matching OptiX implementation. The next OptiX goal should not merely reuse the
host-indexed CSR expansion helpers; it should encode graph edges into RT
geometry, issue source-column rays, and return compact native summaries or row
buffers with explicit phase accounting.
