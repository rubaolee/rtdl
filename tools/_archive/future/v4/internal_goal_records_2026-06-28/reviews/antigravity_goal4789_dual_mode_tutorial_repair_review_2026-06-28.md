# Review Result: Goal4789 Dual-Mode Tutorial Repair

- **Date:** 2026-06-28
- **Verdict:** `approve_goal4789_dual_mode_tutorial_repair_continue`

This document details the critical review of the Goal4789 Dual-Mode Tutorial Repair based on the implementation record, tutorial pages, and example programs.

---

## Review Target

- **Call for Review:** [call_for_review_goal4789_dual_mode_tutorial_repair_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reviews/call_for_review_goal4789_dual_mode_tutorial_repair_2026-06-28.md)
- **Primary Implementation Record:** [goal4789_dual_mode_tutorial_repair_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/engineering/goal4789_dual_mode_tutorial_repair_2026-06-28.md)
- **Changed Tutorial Pages & Index:**
  - [04_relations_and_operators.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/04_relations_and_operators.md)
  - [05_fixed_radius_neighbors.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/05_fixed_radius_neighbors.md)
  - [06_nearest_witness.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/06_nearest_witness.md)
  - [07_aabb_predicates.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/07_aabb_predicates.md)
  - [README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/README.md)
- **Changed Tutorial Programs & Index:**
  - [fixed_radius_neighbors.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/fixed_radius_neighbors.py)
  - [nearest_neighbor.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/nearest_neighbor.py)
  - [aabb_spatial_index_predicates.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/aabb_spatial_index_predicates.py)
  - [README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/README.md)

---

## Review Questions & Explicit Answers

### 1. Does the repair correctly demote `plan_operator_request_v4` from beginner programming model to V4 execution/planning surface?
**Yes.** 
In the revised tutorial pages—specifically [04_relations_and_operators.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/04_relations_and_operators.md), [05_fixed_radius_neighbors.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/05_fixed_radius_neighbors.md), [06_nearest_witness.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/06_nearest_witness.md), and [07_aabb_predicates.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/07_aabb_predicates.md)—the `plan_operator_request_v4` call is systematically demoted to a secondary role. 
The tutorials clarify that V4 planning is for execution targeting, backend selection (e.g. Torch, Numba, RTDL Native), route optimization, and device-array control. It is explicitly positioned after the core RTDL kernel model is established, ensuring that beginners do not mistake execution planning for the primary language model.

### 2. Do the repaired files teach RTDL kernel thinking before V4 operator/runtime API?
**Yes.** 
Every tutorial introduces the target relationship concept (e.g., query point representation, probe/build side roles, candidates produced by traversal, and refinement predicates) before introducing the V4 runner. 
- In [04_relations_and_operators.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/04_relations_and_operators.md), relations and the `input -> traverse -> refine -> emit` ladder are taught first.
- In [05_fixed_radius_neighbors.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/05_fixed_radius_neighbors.md), [06_nearest_witness.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/06_nearest_witness.md), and [07_aabb_predicates.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/07_aabb_predicates.md), the "@rt.kernel" code block (or containment approximation) is presented immediately to teach the language shape, followed by step-by-step table mapping definitions. Only afterward is the user shown the corresponding V4 planner command.

### 3. Does fixed-radius preserve the historical v2.x/v2.14 kernel model rather than replacing it with a planner call?
**Yes.** 
The kernel defined in [fixed_radius_neighbors.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/fixed_radius_neighbors.py) (and described in the corresponding tutorial) preserves the actual historical v2.x/v2.14 `@rt.kernel` syntax and execution model:
```python
@rt.kernel(backend="rtdl", precision="float_approx")
def fixed_radius_neighbors_kernel():
    query_points = rt.input("query_points", rt.Points, role="probe")
    search_points = rt.input("search_points", rt.Points, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=0.5, k_max=3))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])
```
The program runs this compiled kernel directly using the CPU reference path (`rt.run_cpu_python_reference`), validating its correctness. The V4 planner call `plan_operator_request_v4` is kept separate under the `--mode v4` execution path and does not interfere with or replace the core kernel definition.

### 4. Does nearest witness teach candidate rows and argmin/top-k continuation?
**Yes.** 
In [06_nearest_witness.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/06_nearest_witness.md) and [nearest_neighbor.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/nearest_neighbor.py), nearest witness logic is taught through the generation of candidate rows followed by continuation logic.
The `--mode visible` execution path in the script explicitly prints out the raw candidate distance rows and performs the manual per-query `argmin` step:
```python
best = min(rows_for_query, key=lambda row: (row["distance_sq"], row["candidate_id"]))
```
The kernel uses `rt.knn_rows(k=1)` to express this selection filter, making the link between candidate rows and continuation-driven filtering concrete.

### 5. Is the AABB limitation handled honestly without inventing unsupported kernel API?
**Yes.** 
The limitation is handled with complete honesty. Both [07_aabb_predicates.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/07_aabb_predicates.md) and [aabb_spatial_index_predicates.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/aabb_spatial_index_predicates.py) explicitly note that the public kernel API currently lacks a direct `rt.aabb_index_query(...)` predicate.
Instead of fabricating a fake API, they teach broadphase thinking using rectangle-containment via polygon vertices and the `point_in_polygon` predicate, then explain that the V4 `aabb_index_query` is a prepared runner for handling point, range-containment, and range-intersection AABB operations at the execution level.

### 6. Are the examples runnable and educational rather than JSON dumps with release jargon?
**Yes.** 
All three example programs run successfully:
- They accept `--mode kernel`, `--mode v4`, `--mode visible`, and `--mode both` parameters.
- `--mode kernel` outputs the compiled kernel summary and output rows from CPU reference execution.
- `--mode visible` prints the manual python data flow (e.g. coordinates, candidates, bounding logic) to help students trace the raw coordinates to row outcomes.
- `--mode both` maps kernel output side-by-side with V4 operator planning details to demonstrate semantic equivalence.
The JSON output is formatted cleanly and serves as a tool for step-by-step tracing of coordinates, candidate check records, and output relation rows.

### 7. Are there remaining blockers before continuing the tutorial cleanup?
**No.** 
All 21 unittests pass successfully on Windows and Linux (`Ran 21 tests in 66.048s -> OK`). The tutorials compile and run without syntax or reference errors, and structural links resolve correctly.

---

## Verdict Summary

The repaired files restore the correct educational hierarchy (Kernel Thinking first, V4 execution targeting second) and ensure conceptual accuracy while maintaining complete test suite pass rates. The spatial-primitives batch and tutorial cleanup can continue.

> [!IMPORTANT]
> **Non-Authorization Warning:** This review does **not** authorize any release tags, public performance claims, broad V4 speedup assertions, Tier-3 callback claims, raw OptiX callback claims, benchmark/paper-reproduction claims, or similar production claims. It strictly reviews the repaired tutorial teaching model.
