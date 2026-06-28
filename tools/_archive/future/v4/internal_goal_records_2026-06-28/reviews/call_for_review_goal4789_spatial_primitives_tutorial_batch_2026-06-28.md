# Call For Review: Goal4789 Spatial Primitives Tutorial Batch

Date: 2026-06-28

## Requested Verdict Labels

Please return exactly one verdict label:

- `approve_goal4789_spatial_primitives_tutorial_batch_complete`
- `approve_with_required_amendments`
- `block_goal4789_spatial_primitives_batch`

## Files To Review

Primary implementation:

- `examples/tutorial_programs/aabb_spatial_index_predicates.py`
- `examples/tutorial_programs/point_in_polygon.py`
- `examples/tutorial_programs/spatial_join_lsi.py`
- `tutorials/current/07_aabb_predicates.md`
- `tutorials/current/08_point_in_polygon.md`
- `tutorials/current/09_line_segment_intersection_spatial_join.md`

Navigation and command surfaces:

- `examples/tutorial_programs/README.md`
- `examples/README.md`
- `docs/public_documentation_map.md`
- `tutorials/current/README.md`

Engineering record:

- `docs/engineering/goal4789_dual_mode_tutorial_repair_2026-06-28.md`
- `docs/engineering/goal4789_spatial_primitives_tutorial_batch_2026-06-28.md`

Prior external review for the prerequisite repair:

- `docs/reviews/antigravity_goal4789_dual_mode_tutorial_repair_review_2026-06-28.md`

## What Changed

Goal4789 repairs the spatial-primitives tutorials so they teach RTDL kernel
thinking first and V4 operator/runtime mapping second.

Specific outputs:

- PIP now has a real `@rt.kernel` path:
  `rt.input(points) -> rt.traverse(points, polygons) -> rt.refine(point_in_polygon) -> rt.emit(...)`.
- LSI/spatial join now has a real `@rt.kernel` path:
  `rt.input(left_segments/right_segments) -> rt.traverse(...) -> rt.refine(segment_intersection) -> rt.emit(...)`.
- Both examples support `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both`.
- The tutorials explain that V4 `aabb_index_query` is a prepared broadphase/candidate-generation surface, not a black-box app solver.
- Public command lists now use `--mode both` for the dual-mode examples.

## Validation To Consider

Windows validation:

```text
py -3 examples\tutorial_programs\point_in_polygon.py --mode both
py -3 examples\tutorial_programs\spatial_join_lsi.py --mode both
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Observed result:

```text
Ran 21 tests in 71.224s
OK
```

Linux clean-copy validation on `192.168.1.20`:

```text
cd /tmp/rtdl_goal4789_spatial
PYTHONPATH=src:. python3 examples/tutorial_programs/point_in_polygon.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/spatial_join_lsi.py --mode both
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Observed result:

```text
Ran 21 tests in 27.727s
OK
```

## Required Review Questions

1. Does the PIP tutorial now teach the RTDL kernel relation before the V4 runtime surface?
2. Does the LSI/spatial-join tutorial now teach the RTDL kernel relation before the V4 runtime surface?
3. Are `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both` implemented coherently for the repaired programs?
4. Is the V4 `aabb_index_query` wording honest: broadphase/candidate-generation route, not full exact app semantics?
5. Are the snippets and commands suitable for a first-time user path?
6. Are public links and command lists consistent with the repaired programs?
7. Is there any remaining blocker before moving to the next tutorial batch?

## Non-Authorization

This review must not authorize:

- a new release claim;
- a new performance claim;
- a broad V4-over-V2/V3 speedup claim;
- Tier-3 arbitrary callback support;
- raw OptiX callback support;
- C ABI, embedding, or non-Python host claims;
- full paper-reproduction support;
- any app-specific native-kernel exception.
