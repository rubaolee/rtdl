# Goal649 Claude Review — 2026-04-20

## Verdict: ACCEPT

## What was reviewed

Four app rewrites and their test suite:

- `examples/rtdl_robot_collision_screening_app.py`
- `examples/rtdl_hausdorff_distance_app.py`
- `examples/rtdl_outlier_detection_app.py`
- `examples/rtdl_dbscan_clustering_app.py`
- `tests/goal649_app_rewrite_anyhit_reduce_rows_test.py`

## Findings

**`ray_triangle_any_hit` usage (robot app):** The kernel correctly calls
`rt.ray_triangle_any_hit(exact=False)` inside `rt.refine(...)` and emits
`["ray_id", "any_hit"]`. The oracle uses `rt.ray_triangle_any_hit_cpu`.
No residual `hit_count` field is emitted. The test explicitly asserts
`"hit_count" not in row` for all rows.

**`rt.reduce_rows` usage — all four apps:**

| App | op | group_by | output_field | Correct? |
|-----|----|----------|--------------|---------|
| robot collision | `"any"` | `"pose_id"` | `"collides"` | yes |
| hausdorff | `"max"` | (none — global per direction) | `"directed_distance"` | yes |
| outlier detection | `"count"` | `"query_id"` | `"neighbor_count"` | yes |
| DBSCAN | `"count"` | `"query_id"` | `"neighbor_count"` | yes |

The Hausdorff ungrouped max is correct: `_directed_from_rows` receives rows
for a single directed pass (A→B or B→A), so a global max is the directed
Hausdorff distance.

**Honesty boundary — no overclaiming:** A grep across all four app files for
`native.*speedup`, `acceleration`, and `native.*any.hit` returned no matches.
The `rtdl_role` fields accurately describe the layering: RTDL emits rows,
`reduce_rows` aggregates, Python owns application logic. The `boundary` fields
in robot and outlier apps explicitly disclaim continuous collision detection,
full kinematics, and native density primitives.

**Oracle verification:** Every `run_app` returns a `matches_oracle` boolean and
the four tests assert it `True`. The robot and outlier/DBSCAN oracles are
independent Python implementations (`rt.ray_triangle_any_hit_cpu`,
brute-force loops), not the same code path as the RTDL kernel.

**Test quality:** Tests check correctness (`matches_oracle`), structural
correctness (`any_hit` present, `hit_count` absent), specific fixture
expectations (`colliding_pose_ids == [2, 3]`, `outlier_point_ids == [7, 8]`,
`cluster_sizes == {1: 4, 2: 3}`), and `rtdl_role` string content.

## No issues found

All rewritten apps correctly adopt the v0.9.5 programming model, the
`reduce_rows` calls match their semantic intent, no native speedup is claimed,
and the test suite provides meaningful coverage.
