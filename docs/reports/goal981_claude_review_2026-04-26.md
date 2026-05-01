# Goal981 Claude Review — Embree Graph Correctness Repair (Re-review)

Date: 2026-04-26
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

---

## Scope

This re-review supersedes the earlier draft. The pad was raised from `1e-3` to `2.5e-1` after same-scale probing, and a large-scale analytic test at `copies=20000` was added to `goal903_embree_graph_ray_traversal_test.py`. Three questions are addressed:

1. Does the `0.25` candidate pad remain a conservative correctness fix because exact callbacks are unchanged?
2. Does the large-scale analytic test at `copies=20000` justify the larger pad?
3. Is the residual risk performance false-candidate overhead rather than correctness overclaim?

---

## Finding 1: The 0.25 Pad Is Still Conservative — Exact Callbacks Are Unchanged

`src/native/embree/rtdl_embree_scene.cpp` line 37:

```cpp
constexpr float kBvhCandidatePad = 2.5e-1f;
```

The pad is applied in exactly two places:

- `graph_edge_point_bounds` (lines 609–618): all six Embree bound axes padded by `kBvhCandidatePad`.
- `triangle_bounds` (lines 632–642): all six bound axes padded by `kBvhCandidatePad`.

The exact acceptance callbacks are unchanged:

- `graph_edge_point_intersect` (lines 733–765): accepts only edges where `edge_point.src_vertex == frontier_vertex->vertex_id` and the destination is unvisited. This is a pure graph-connectivity predicate with no geometric component. A wider BVH box can deliver more edge-point primitives to the callback, but only those matching `src_vertex` and `dst_vertex` visited state are accepted.
- `triangle_intersect` (lines 910–924): calls `finite_ray_hits_triangle(*state->ray, triangle)` — the exact 2D ray–triangle predicate.
- `triangle_occluded` (lines 926–938): same exact predicate, terminates the ray on acceptance.

The architecture is the standard RT conservative-traversal pattern: BVH bounds deliver candidates; callbacks decide acceptance. Widening bounds can only *add* false candidates, never drop true ones. Callbacks are unchanged, so no previously accepted row can be dropped and no new row can be incorrectly accepted. The fix is sound regardless of pad magnitude.

`triangle_bounds_3d` (lines 644–654) correctly does **not** apply the pad — 3D triangles have genuine Z extent and do not need it.

---

## Finding 2: The Large-Scale Analytic Test Justifies the Larger Pad

The earlier `1e-3` pad was correct in principle but insufficient in practice. Goal980 showed that at copies=256 (and larger), BFS and triangle_count stopped finding all candidates — the BVH bounds were too thin for planar custom user geometry at the coordinate ranges reached during replication. Raising the pad to `2.5e-1` solves this at the tested scales.

The new test `test_unified_graph_app_embree_large_summary_matches_analytic_counts` in `goal903_embree_graph_ray_traversal_test.py` (lines 81–94) runs at `copies=20000` and checks exact analytic counts:

| Metric | Expected | Relationship to copies |
| --- | ---: | --- |
| `bfs.discovered_edge_count` | 40 000 | `2 × copies` |
| `bfs.discovered_vertex_count` | 40 000 | `2 × copies` |
| `triangle_count.triangle_count` | 20 000 | `copies` |
| `triangle_count.touched_vertex_count` | 60 000 | `3 × copies` |
| `visibility_edges.visible_edge_count` | 20 000 | `copies` |
| `visibility_edges.blocked_edge_count` | 60 000 | `3 × copies` |

This is a strong verification. The test uses analytic ground truth, not just Embree-vs-CPU comparison, so it cannot pass by symmetric cancellation of errors. At 20 000 copies the BVH contains at least 40 000 graph edge-point primitives; all must be reachable during traversal or counts undercount. The test passing confirms the pad is sufficient at this scale.

Combined with Goal980's per-copy-scale audit (1, 2, 8, 16, 256 — all `ok`, 0 mismatches) and the existing goal903 tests at copies=4 and copies=16, correctness is verified across more than three orders of magnitude of graph scale.

---

## Finding 3: Residual Risk Is Performance Overhead, Not Correctness Overclaim

The only remaining concern is that `2.5e-1` is a large geometric pad relative to typical floating-point epsilons. In dense graphs where edge-point positions are packed closer than 0.5 units apart, the BVH will deliver many false-candidate callbacks to `graph_edge_point_intersect`. Each such callback reads `edge_point.src_vertex`, compares it to `frontier_vertex->vertex_id`, and returns immediately on mismatch — work is done but no row is accepted incorrectly.

This is a performance-overhead risk, not a correctness risk:

- More callbacks per BFS step → more CPU cycles, not wrong answers.
- The Graph980 timing at copies=256 shows Embree at 0.009 s vs CPU at 0.669 s, leaving substantial headroom even with callback overhead.
- `graph_analytics / graph_visibility_edges_gate` is already classified `needs_timing_baseline_repair` in Goal978 — it will not enter any public speedup-claim review until a comparable timing baseline exists. That baseline work will naturally expose any density-driven callback overhead.

There is no path through which the wider pad produces a false accepted row or inflates a correctness claim.

---

## Finding 4: Public RTX Speedup Claims Remain Unauthorized

Goal978 (post-repair regeneration) authorizes zero public speedup claims across all 17 rows. The graph_analytics row carries:

- recommendation: `needs_timing_baseline_repair`
- `public speedup authorized: False`
- reason: no non-OptiX same-semantics baseline exposes a positive comparable phase

No row was promoted by this correctness repair. The claim boundary is intact.

---

## Summary

| Question | Answer |
| --- | --- |
| Is `0.25` pad still conservative? | Yes — exact callbacks are the sole decision layer; pad only adds false candidates |
| Does the large-scale analytic test justify the change? | Yes — exact analytic counts verified at 20 000 copies across 6 metrics |
| Is residual risk performance overhead rather than correctness overclaim? | Yes — extra callbacks are discarded by graph predicates; no wrong rows accepted |
| Are public RTX speedup claims unauthorized? | Confirmed — 0 claims authorized; graph row remains at `needs_timing_baseline_repair` |

---

## Verdict

**ACCEPT**

The widened BVH candidate pad (`2.5e-1`) is a correct and conservative repair for the traversal-candidate-loss failure mode identified in Goal980. The large-scale analytic test at `copies=20000` provides adequate justification for the pad magnitude. The residual risk is false-candidate callback overhead during future high-density graph workloads, not any form of correctness overclaim. Zero public RTX speedup claims are authorized; the claim boundary is unchanged.
