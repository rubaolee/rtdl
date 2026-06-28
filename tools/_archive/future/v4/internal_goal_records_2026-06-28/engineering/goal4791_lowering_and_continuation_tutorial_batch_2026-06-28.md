# Goal4791 lowering and continuation tutorial batch

Date: 2026-06-28

## Purpose

Goal4791 extends the V4 tutorial program sequence with the next three learning bridges after ray hits and grouped continuations:

1. component union from fixed-radius rows,
2. bounded witness collection from emitted witness rows,
3. aggregate-frontier rows with weighted grouped continuation.

The user-facing intent is explicit: each lesson must teach the RTDL row/relation model first, then show how the V4 operator/runtime surface carries the same shape. The V4 wrapper is not allowed to replace the explanation.

## Files changed

| File | Action | Why it exists |
| --- | --- | --- |
| `examples/tutorial_programs/component_union_from_radius.py` | Rewritten as a runnable dual-mode tutorial program. | Teaches fixed-radius neighbor rows, core-point detection, union edges, and component labels before showing the V4 `component_union` surface. |
| `examples/tutorial_programs/bounded_witness_collection.py` | Rewritten as a runnable dual-mode tutorial program. | Teaches witness rows, bounded per-pair collection, overflow validation, and the V4 closest-witness grouped-argmin mapping. |
| `examples/tutorial_programs/aggregate_frontier_rows.py` | Rewritten as a relation-first tutorial program. | Teaches aggregate-or-exact frontier rows and weighted grouped continuation. It explicitly does not fake an `@rt.kernel` surface that the public tutorial API does not expose. |
| `tutorials/current/12_component_union_from_radius.md` | Added. | Step-by-step lesson for turning radius-neighbor rows into components. |
| `tutorials/current/13_bounded_witness_collection.md` | Added. | Step-by-step lesson for turning hit/witness rows into bounded result rows. |
| `tutorials/current/14_aggregate_frontier_rows.md` | Added. | Step-by-step lesson for aggregate frontier rows and weighted continuation. |
| `tutorials/current/README.md` | Updated. | Adds the three new lessons to the current tutorial path. |
| `examples/tutorial_programs/README.md` | Updated. | Adds commands for the three new tutorial programs and removes duplicate stale bounded-witness listing. |
| `examples/README.md` | Updated. | Adds the new tutorial program quick path. |
| `docs/public_documentation_map.md` | Updated. | Adds the three new scripts to the public quick-check path. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Updated. | Adds lessons 12, 13, and 14 to the public documentation gate. |

## Teaching contract

### Component union

The kernel mode compiles a real RTDL tutorial kernel that emits radius-neighbor rows:

```python
@rt.kernel(name="radius_edges_kernel", precision="float_approx")
def radius_edges_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.55, k_max=8))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])
```

The continuation then filters self-neighbors, counts radius rows, marks core points, emits union edges, and computes component labels. The V4 mode is only introduced after that row shape is visible.

### Bounded witness collection

The kernel mode compiles a real RTDL tutorial kernel that emits segment witness rows:

```python
@rt.kernel(name="segment_witness_rows_kernel", precision="float_approx")
def segment_witness_rows_kernel():
    left_segments = rt.input("left_segments", rt.Segments, role="probe")
    right_segments = rt.input("right_segments", rt.Segments, role="build")
    candidates = rt.traverse(left_segments, right_segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])
```

The continuation keeps a bounded number of witnesses per pair and reports overflow. The V4 closest-witness grouped-argmin surface is presented as the measured runtime mapping for the recognized row pattern.

### Aggregate frontier

This lesson is intentionally relation-first. The current public tutorial API does not expose aggregate frontier as an `@rt.kernel` predicate, so the program does not pretend otherwise. It teaches the row relation:

```text
bodies + aggregate cells
  -> aggregate-or-exact frontier rows
  -> weighted contribution rows
  -> grouped vector force rows
```

Then it shows the V4 prepared frontier surface plus the explicit CuPy grouped-sum continuation as the implementation mapping for that relation.

## Validation

### Windows workspace

Commands:

```powershell
py -3 examples\tutorial_programs\component_union_from_radius.py --mode kernel
py -3 examples\tutorial_programs\bounded_witness_collection.py --mode kernel
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode relation
py -3 examples\tutorial_programs\aggregate_frontier_rows.py --mode v4
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 84.224s
OK
```

The Windows Python process printed the known local prefix warning on some runs, but all commands exited successfully.

### Local Linux clean-copy simulation

Host: `192.168.1.20`

The workspace was copied to `/tmp/rtdl_goal4791_lowering` and run as a clean user checkout with `PYTHONPATH=src:.`.

Commands:

```bash
PYTHONPATH=src:. python3 examples/tutorial_programs/component_union_from_radius.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/bounded_witness_collection.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/aggregate_frontier_rows.py --mode both
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 32.212s
OK
```

The three tutorial program outputs were valid JSON and returned `status: "ok"`.

## Non-claims

This goal does not authorize:

- a V4 public tag,
- broad V4 speedup wording,
- whole-app performance claims,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims,
- paper-reproduction claims,
- app-specific native-kernel claims.

## Goal status

Implementation and Windows/Linux validation are complete. External review is required before marking the goal complete.
