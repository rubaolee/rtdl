# Goal 265 Report: v0.5 RTNN Dataset Registry

Date: 2026-04-12
Status: implemented

## Purpose

Add a first-class RTNN-specific dataset-family and experiment-target registry so
the `v0.5` paper-consistency line has a concrete internal source of truth for
dataset scope and reproduction-tier labeling.

## What Landed

### New module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_reproduction.py`

Added:

- `RtnnDatasetFamily`
- `RtnnExperimentTarget`
- `RtnnLocalProfile`
- `RTNN_DATASET_FAMILIES`
- `RTNN_EXPERIMENT_TARGETS`
- `RTNN_LOCAL_PROFILES`
- `rtnn_dataset_families(...)`
- `rtnn_experiment_targets(...)`
- `rtnn_local_profiles(...)`

### Public surface update

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported the new RTNN registry types and query helpers.

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal265_v0_5_rtnn_dataset_registry_test.py`

The test slice verifies:

- the expected three RTNN dataset families are present
- all registered families are explicitly 3D
- dataset-handle filtering works
- reproduction-tier labels distinguish:
  - bounded reproduction
  - exact reproduction candidate
  - RTDL extension
- bounded targets point at the new `bounded_knn_rows` line
- bounded local profiles exist for each family

### Sequence correction

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/v0_5_goal_sequence_2026-04-11.md`

The sequence now reflects the real line:

1. Goal 258 charter
2. Goal 259 3D design
3. Goal 260 3D public/reference support
4. Goal 261 native 3D contract hardening
5. Goal 262 bounded-radius KNN contract
6. Goal 263 bounded KNN surface
7. Goal 264 bounded KNN CPU/oracle
8. Goal 265 RTNN dataset registry
9. Goal 266 baseline-library harness decisions
10. Goal 267 reproduction matrix

## Verification

Executed:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal265_v0_5_rtnn_dataset_registry_test \
  tests.goal263_v0_5_bounded_knn_rows_surface_test \
  tests.goal264_v0_5_bounded_knn_rows_cpu_oracle_test
```

Result:

- `Ran 13 tests in 0.022s`
- `OK`

## Honesty Boundary

This goal does not claim:

- actual dataset downloads
- exact RTNN dataset packaging
- baseline-library closure
- paper-faithful reproduction

It only makes the dataset and reproduction-tier layer explicit so later
`v0.5` work can be scoped honestly.
