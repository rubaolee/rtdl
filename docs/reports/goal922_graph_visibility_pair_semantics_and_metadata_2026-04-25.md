# Goal922: Graph Visibility Pair Semantics and Metadata

Date: 2026-04-25

## Result

Goal922 fixes a local graph test and metadata mismatch after the `visibility_pair_rows(...)` contract change.

The graph app now marks the top-level unified payload as:

```text
rt_core_accelerated = true
```

only for:

```text
backend = optix
scenario = visibility_edges
```

This matches the existing section-level behavior and the `--require-rt-core` gate.

## Correctness Fix

The stale graph honesty test expected `visible_edge_count = 7` for `copies=2`, which reflected the older Cartesian observer-target behavior. After the Goal913/915 contract change, `visibility_edges` uses explicit candidate-pair semantics through `visibility_pair_rows(...)`.

For `copies=2`, the correct summary is:

```text
visible_edge_count = 2
blocked_edge_count = 6
row_count = 8
```

The test now asserts the explicit-pair result.

## Boundary

This is not a graph readiness promotion. `graph_analytics` still requires a real RTX artifact for:

- `optix_visibility_anyhit`
- `optix_native_graph_ray_bfs`
- `optix_native_graph_ray_triangle_count`

BFS frontier/visited bookkeeping and triangle set-intersection remain outside the RT-core claim.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal889_graph_visibility_optix_gate_test
```

Result: `14 tests OK`.
