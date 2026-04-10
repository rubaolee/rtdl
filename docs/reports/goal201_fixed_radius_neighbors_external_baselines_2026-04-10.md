# Goal 201 Fixed-Radius Neighbors External Baselines

## Summary

Goal 201 adds the first external baseline harness for the `v0.4`
`fixed_radius_neighbors` workload.

The first required external CPU baseline is now a checked-in SciPy `cKDTree`
helper. A bounded PostGIS helper also exists for the same workload, with a
strictly limited role: moderate-scale comparison and familiar SQL-oriented
validation. Neither dependency is required for the normal RTDL first-run path.

## Files Reviewed / Revised

- `src/rtdsl/external_baselines.py`
  - added optional SciPy and PostGIS baseline helpers
- `src/rtdsl/baseline_runner.py`
  - added `scipy` and `postgis` backend support
- `src/rtdsl/__init__.py`
  - exported the new external-baseline helpers
- `tests/goal201_fixed_radius_neighbors_external_baselines_test.py`
  - added authored, Natural Earth, runner, and SQL-shape coverage
- `docs/features/fixed_radius_neighbors/README.md`
  - updated implementation-status and optional-baseline language
- `docs/goal_201_fixed_radius_neighbors_external_baselines.md`
  - recorded scope and acceptance

## Design Decisions

### SciPy

The SciPy baseline uses `scipy.spatial.cKDTree.query_ball_point(...)` and then
re-applies RTDL’s exact public semantics:

- exact `distance <= radius`
- per-query sort by `distance`, then `neighbor_id`
- truncate after ordering to `k_max`
- final global sort by `query_id`

This avoids letting SciPy’s raw return order become the public contract.

### PostGIS

The PostGIS helper is intentionally bounded:

- temp-table load of query/search points
- `ST_DWithin` as the candidate predicate
- `ST_Distance` plus `ROW_NUMBER() OVER (...)` for deterministic top-`k`
  behavior
- final `ORDER BY query_id, distance, neighbor_id`

This is enough to support moderate comparison runs and SQL-backed validation
without making PostGIS the truth path or implementation model.

## Honesty Boundary

- the RTDL truth path remains:
  - Python reference
  - native CPU/oracle
- external baselines are comparison tools
- SciPy and PostGIS remain optional dependencies
- this goal does not claim performance wins

## Verification

- `PYTHONPATH=src:. python3 -m unittest tests.goal201_fixed_radius_neighbors_external_baselines_test tests.goal200_fixed_radius_neighbors_embree_test tests.goal199_fixed_radius_neighbors_cpu_oracle_test tests.goal198_fixed_radius_neighbors_truth_path_test`
- `python3 -m compileall src/rtdsl tests/goal201_fixed_radius_neighbors_external_baselines_test.py`

## Outcome

`fixed_radius_neighbors` now has:

- public contract
- DSL surface
- Python truth path
- native CPU/oracle path
- Embree path
- external SciPy baseline harness
- bounded PostGIS comparison helper

That is enough to move `v0.4` from “first working workload” to “first working
workload with an external comparison story.”
