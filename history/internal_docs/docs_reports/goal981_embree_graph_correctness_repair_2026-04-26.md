# Goal981 Embree Graph Correctness Repair

Date: 2026-04-26

Goal981 repairs the native Embree graph and 2D visibility traversal correctness issue found by Goal980. It does not collect cloud timings and does not authorize public RTX speedup claims.

## Problem

Goal980 showed that `graph_analytics` diverged between CPU reference and Embree at replicated-copy scales:

- `bfs` and `triangle_count` stopped scaling in Embree at larger copy counts.
- `visibility_edges` reported false visibility because some blocker triangles were not visited.
- The failure pattern was traversal-candidate loss, not exact predicate failure: callbacks were correct when invoked, but the BVH bounds were too thin for planar custom user geometry.

## Repair

The native Embree scene code now separates candidate bounds from exact acceptance:

- `src/native/embree/rtdl_embree_scene.cpp` adds `kBvhCandidatePad = 2.5e-1f`.
- Graph edge-point user-geometry bounds use the wider candidate pad.
- 2D triangle user-geometry bounds use the wider candidate pad.
- Segment bounds receive a small epsilon pad.
- Exact callbacks still enforce the original graph/visibility predicates, so the wider BVH bounds may add candidates but must not change accepted rows.

This is the intended RT pattern: use BVH traversal conservatively to avoid missing candidates, then apply exact predicates in the callback/filter/refinement layer.

## Verification

Forced native rebuild and focused tests:

```text
RTDL_FORCE_EMBREE_REBUILD=1 PYTHONPATH=src:. python3 -m unittest \
  tests.goal903_embree_graph_ray_traversal_test \
  tests.goal980_graph_baseline_correctness_audit_test
```

Result:

```text
Ran 9 tests in 6.738s
OK
```

Goal980 regenerated after the repair:

| Copies | CPU sec | Embree sec | Status |
| ---: | ---: | ---: | --- |
| 1 | 0.010130 | 0.010823 | `ok` |
| 2 | 0.000179 | 0.000256 | `ok` |
| 8 | 0.000752 | 0.000466 | `ok` |
| 16 | 0.002487 | 0.000743 | `ok` |
| 256 | 0.669467 | 0.009488 | `ok` |

An additional large-scale analytic Embree summary check at `copies=20000` verifies:

- `bfs.discovered_edge_count = 40000`
- `bfs.discovered_vertex_count = 40000`
- `triangle_count.triangle_count = 20000`
- `triangle_count.touched_vertex_count = 60000`
- `visibility_edges.visible_edge_count = 20000`
- `visibility_edges.blocked_edge_count = 60000`

Goal978 regenerated after the repair:

- `graph_analytics / graph_visibility_edges_gate` moved from `needs_graph_correctness_repair` to `needs_timing_baseline_repair`.
- Public RTX speedup claims authorized here remain `0`.

## Remaining Work

Graph correctness is repaired locally for the audited Embree path. The graph row still needs same-scale timing-baseline repair before it can enter any public speedup-claim review. Public RTX claims remain blocked until separate 2-AI claim review with adequate scale and repeat evidence.
