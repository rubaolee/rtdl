# Review Result: Goal4789 Spatial Primitives Tutorial Batch

- **Date:** 2026-06-28
- **Verdict:** `approve_goal4789_spatial_primitives_tutorial_batch_complete`

This document details the external review of the RTDL V4 Goal4789 Spatial Primitives Tutorial Batch.

---

## Review Target Files

- **Call for Review:** [call_for_review_goal4789_spatial_primitives_tutorial_batch_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reviews/call_for_review_goal4789_spatial_primitives_tutorial_batch_2026-06-28.md)
- **Primary Implementations:**
  - [point_in_polygon.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/point_in_polygon.py)
  - [spatial_join_lsi.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/spatial_join_lsi.py)
  - [aabb_spatial_index_predicates.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/aabb_spatial_index_predicates.py)
- **Tutorial Pages:**
  - [08_point_in_polygon.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/08_point_in_polygon.md)
  - [09_line_segment_intersection_spatial_join.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/09_line_segment_intersection_spatial_join.md)
  - [07_aabb_predicates.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/07_aabb_predicates.md)
- **Navigation & Command Indexes:**
  - [examples/tutorial_programs/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/README.md)
  - [examples/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/README.md)
  - [docs/public_documentation_map.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/public_documentation_map.md)
  - [tutorials/current/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/README.md)
- **Engineering Record:**
  - [goal4789_spatial_primitives_tutorial_batch_2026-06-28.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/engineering/goal4789_spatial_primitives_tutorial_batch_2026-06-28.md)

---

## Required Review Questions & Detailed Answers

### 1. Does the PIP tutorial now teach the RTDL kernel relation before the V4 runtime surface?
**Yes.**
The revised tutorial [08_point_in_polygon.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/08_point_in_polygon.md) has been structured around a "Kernel Shape" first layout. It introduces the `@rt.kernel` definition (`point_in_polygon_kernel`), highlighting the probe (`rt.Points`) and build (`rt.Polygons`) inputs, broadphase candidate traversal (`rt.traverse`), and containment refinement (`rt.refine` with `rt.point_in_polygon`). The V4 planner command (`plan_operator_request_v4`) is introduced at the end under "V4 Runtime Mapping" and is explicitly demoted to a secondary role as an execution surface mapping, ensuring beginners do not mistake it for the primary programming model.

### 2. Does the LSI/spatial-join tutorial now teach the RTDL kernel relation before the V4 runtime surface?
**Yes.**
Similar to the PIP page, [09_line_segment_intersection_spatial_join.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/09_line_segment_intersection_spatial_join.md) presents the `@rt.kernel` shape first (`line_segment_intersection_kernel`), teaching the inputs, BVH-based broadphase traversal, refinement via segment-pair intersection (`rt.segment_intersection`), and emission of witness coordinates. The V4 `plan_operator_request_v4` execution target is only shown later under "V4 Runtime Mapping," after the user is thoroughly grounded in the relational model.

### 3. Are `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both` implemented coherently for the repaired programs?
**Yes.**
Both [point_in_polygon.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/point_in_polygon.py) and [spatial_join_lsi.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/spatial_join_lsi.py) support these four modes cleanly:
- `--mode kernel` compiles and executes the core RTDL kernel with the CPU reference backend and outputs relation rows.
- `--mode visible` mirrors the containment/overlap math directly in plain Python, demonstrating the coordinate filtering step-by-step.
- `--mode v4` showcases the V4 prepared operator execution plan for the target relation.
- `--mode both` executes all modes side-by-side in a structured JSON payload to prove semantic equivalence.

### 4. Is the V4 `aabb_index_query` wording honest: broadphase/candidate-generation route, not full exact app semantics?
**Yes.**
The tutorials and tutorial scripts are scrupulously honest about this mapping. They explicitly teach that the V4 `aabb_index_query` operator is a prepared broadphase route designed to generate candidate pairs (e.g. bounding box overlaps), rather than a black-box replacement for exact point-in-polygon containment or exact line-segment intersection coordinates. For example, [07_aabb_predicates.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/07_aabb_predicates.md) states clearly that the public kernel API currently lacks a direct `rt.aabb_index_query` predicate, and both [08_point_in_polygon.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/08_point_in_polygon.md) and [09_line_segment_intersection_spatial_join.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/09_line_segment_intersection_spatial_join.md) clarify that the V4 surface does not replace the kernel containment or intersection check, but instead generates candidates for it.

### 5. Are the snippets and commands suitable for a first-time user path?
**Yes.**
The code blocks are clean, self-contained, and copy-pasteable. All paths utilize standard Python paths and execution variables (`PYTHONPATH=src:.`), which run without any external hardware/CUDA requirements.

### 6. Are public links and command lists consistent with the repaired programs?
**Yes.**
The indexing structures—specifically [examples/tutorial_programs/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/README.md), [examples/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/README.md), [docs/public_documentation_map.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/public_documentation_map.md), and [tutorials/current/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/README.md)—have been updated to refer to the `--mode both` variant for these dual-mode programs, ensuring that the first-time user path executes the complete kernel-to-V4 comparison rather than single-mode legacy paths.

### 7. Is there any remaining blocker before moving to the next tutorial batch?
**No.**
Both [point_in_polygon.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/point_in_polygon.py) and [spatial_join_lsi.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/spatial_join_lsi.py) execute cleanly on Windows and output correct JSON relations. Additionally, the complete public-surface unittest suite has been run and completed successfully:
```text
Ran 21 tests in 70.653s
OK
```

---

## Non-Authorization Guardrails

This review strictly governs the educational structure and conceptual hierarchy of the Stage 1 spatial primitives tutorial batch. It **does not** authorize:
- a new release claim;
- a new performance claim;
- a broad V4-over-V2/V3 speedup claim;
- Tier-3 arbitrary callback support;
- raw OptiX callback support;
- C ABI, embedding, or non-Python host claims;
- full paper-reproduction support;
- any app-specific native-kernel exception.
