# Goal 281 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`

## Summary

Goal 281 added a bounded 3D PostGIS path for fixed-radius neighbors.

## What Changed

- `src/rtdsl/external_baselines.py`
  - added `build_postgis_fixed_radius_neighbors_3d_sql(...)`
  - added `prepare_postgis_point3d_tables(...)`
  - added `query_postgis_fixed_radius_neighbors_3d(...)`
  - added `run_postgis_fixed_radius_neighbors_3d(...)`
- `src/rtdsl/__init__.py`
  - exports the new 3D PostGIS fixed-radius helpers
- `tests/goal281_postgis_3d_fixed_radius_baseline_test.py`
  - verifies the SQL shape
  - verifies parity against `fixed_radius_neighbors_cpu(...)`
  - verifies `k_max` handling

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal201_fixed_radius_neighbors_external_baselines_test \
  tests.goal207_knn_rows_external_baselines_test \
  tests.goal281_postgis_3d_fixed_radius_baseline_test

Ran 17 tests
OK
```

Public exports verified:

- `run_postgis_fixed_radius_neighbors_3d`
- `build_postgis_fixed_radius_neighbors_3d_sql`

## Important Boundary

This goal does not claim live PostGIS-backed KITTI validation.

Observed Linux state during this goal:

- `psycopg2` available: yes
- `psql` available: yes
- `RTDL_POSTGIS_DSN`: unset

So the current closure is:

- real repo-side 3D PostGIS support for bounded fixed-radius comparisons
- no live Linux PostGIS execution claim yet

## Result

Goal 281 is complete as a bounded contract/support goal.
