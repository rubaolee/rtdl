# Goal4789 Dual-Mode Tutorial Repair

Date: 2026-06-28

## Why This Repair Exists

The user correctly identified that the current foundation tutorials were
drifting into V4 operator/runtime API teaching:

```python
rtdl_v4.plan_operator_request_v4("fixed_radius", partner="torch")
```

That API is useful, but it is not the RTDL language model. It plans or pins an
execution surface for a recognized operator. It must not replace teaching how a
user expresses a problem as RTDL inputs, traversal, refinement, emitted rows,
and continuation.

## Correct Rule

Every tutorial program should teach:

1. **Kernel mode first**
   - problem to probe/build inputs;
   - `rt.traverse(...)`;
   - `rt.refine(...)`;
   - `rt.emit(...)`;
   - continuation rows when applicable.

2. **V4 mode second**
   - the operator/runtime surface for the same relation;
   - partner choice or route inspection;
   - explicit statement that this is execution control, not the beginner
     programming model.

## Files Repaired

| File | Repair |
| --- | --- |
| `tutorials/current/04_relations_and_operators.md` | Rewritten as kernel-first vocabulary; V4 planner is second. |
| `tutorials/current/05_fixed_radius_neighbors.md` | Rewritten around the real `@rt.kernel` fixed-radius shape. |
| `tutorials/current/06_nearest_witness.md` | Rewritten around candidate rows plus `knn_rows(k=1)` argmin/top-k meaning. |
| `tutorials/current/07_aabb_predicates.md` | Rewritten to honestly distinguish kernel-shaped rectangle containment from the V4 AABB prepared route. |
| `examples/tutorial_programs/fixed_radius_neighbors.py` | Added `--mode kernel`, `--mode v4`, `--mode both`, and `--mode visible`; kernel mode runs RTDL CPU reference. |
| `examples/tutorial_programs/nearest_neighbor.py` | Added the same mode split; kernel mode runs `knn_rows(k=1)`. |
| `examples/tutorial_programs/aabb_spatial_index_predicates.py` | Added mode split; kernel mode teaches rectangle containment with `point_in_polygon`; V4 mode names the true AABB route. |
| `examples/tutorial_programs/README.md` | Reordered wording so V4 quickstart follows kernel concepts. |
| `tutorials/current/README.md` | Added explicit kernel-first, V4-second learning rule. |

## Honest Limitation

The public kernel API currently has direct fixed-radius and nearest-witness
forms (`fixed_radius_neighbors`, `knn_rows`) but not a direct
`aabb_index_query` predicate. The AABB lesson therefore does not pretend to run
a fake AABB kernel. It uses a rectangle-containment kernel-shaped lesson and
then maps to the V4 prepared AABB route.

## Review Packet

Review request:

`docs/reviews/call_for_review_goal4789_dual_mode_tutorial_repair_2026-06-28.md`

## Non-Authorization

This repair does not authorize a release tag, performance claims, broad V4
claims, Tier-3 callback claims, or benchmark/paper-reproduction claims. It only
repairs the teaching model.
