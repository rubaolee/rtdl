# Goal1300: ANN And Facility Generic Fixed-Radius Migration

Date: 2026-05-05

## Purpose

Goal1300 migrates two more prepared OptiX fixed-radius threshold-decision app
paths to the Goal1298 generic wrapper:

- `ann_candidate_search / candidate_threshold_prepared`
- `facility_knn_assignment / coverage_threshold_prepared`

This is an internal v1.5 migration slice. It does not migrate nearest-neighbor
ranking or authorize public speedup wording.

## Change

`ann_candidate_search` now routes the OptiX candidate-coverage decision through:

```text
run_generic_prepared_fixed_radius_threshold_reached_count_2d(...)
```

`facility_knn_assignment` now routes the OptiX service-coverage decision through
the same generic prepared primitive.

Existing app payloads, oracle comparisons, `--require-rt-core` behavior, and
native-continuation metadata are preserved.

## Local Verification

Passed locally:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1300_v1_5_ann_facility_generic_migration_test \
  tests.goal880_ann_candidate_threshold_rt_core_subpath_test \
  tests.goal881_facility_coverage_optix_subpath_test \
  tests.goal955_spatial_prepared_native_continuation_test \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test
```

Result: 27 tests OK.

Passed locally:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_ann_candidate_app.py \
  examples/rtdl_facility_knn_assignment.py \
  tests/goal1300_v1_5_ann_facility_generic_migration_test.py
```

`git diff --check` passed.

## Next Pod Action

Run the migrated OptiX summary paths on the active RTX pod:

```text
PYTHONPATH=src:. python3 examples/rtdl_ann_candidate_app.py \
  --backend optix --copies 1024 \
  --optix-summary-mode candidate_threshold_prepared --require-rt-core

PYTHONPATH=src:. python3 examples/rtdl_facility_knn_assignment.py \
  --backend optix --copies 1024 \
  --optix-summary-mode coverage_threshold_prepared --require-rt-core
```

## Boundary

These are bounded fixed-radius threshold-decision paths only. They do not claim
ANN indexing, nearest-neighbor ranking, KNN fallback assignment, facility
optimization, whole-app acceleration, or public NVIDIA speedup performance.
