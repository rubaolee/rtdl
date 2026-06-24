# Goal1301: Outlier And DBSCAN Generic Fixed-Radius Migration

Date: 2026-05-05

## Purpose

Goal1301 migrates the remaining outlier/DBSCAN fixed-radius threshold summary
paths onto the Goal1298 generic primitive wrapper:

- `outlier_detection / rt_count_threshold`
- `outlier_detection / rt_count_threshold_prepared`
- `dbscan_clustering / rt_core_flags`
- `dbscan_clustering / rt_core_flags_prepared`

This is an internal v1.5 migration slice. It does not claim full outlier
analytics, full DBSCAN cluster expansion, whole-app acceleration, or public
NVIDIA speedup.

## Change

Direct Embree/OptiX fixed-radius threshold summaries now call:

```text
run_generic_fixed_radius_count_threshold_2d(...)
```

Prepared row summaries now use:

```text
prepare_generic_fixed_radius_count_threshold_2d(...)
```

Prepared scalar counts now use:

```text
run_generic_prepared_fixed_radius_threshold_reached_count_2d(...)
```

Existing CLI modes and payload names are preserved.

## Local Verification

Passed locally:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1301_v1_5_outlier_dbscan_generic_migration_test \
  tests.goal695_optix_fixed_radius_summary_test \
  tests.goal757_prepared_optix_fixed_radius_count_test \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test
```

Result:

```text
Ran 28 tests in 0.008s

OK (skipped=2)
```

Passed locally:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_outlier_detection_app.py \
  examples/rtdl_dbscan_clustering_app.py \
  tests/goal1301_v1_5_outlier_dbscan_generic_migration_test.py \
  tests/goal695_optix_fixed_radius_summary_test.py
```

## Next Pod Action

Run the migrated OptiX prepared paths on the active RTX pod:

```text
PYTHONPATH=src:. python3 examples/rtdl_outlier_detection_app.py \
  --backend optix --copies 1024 \
  --optix-summary-mode rt_count_threshold_prepared \
  --output-mode density_count

PYTHONPATH=src:. python3 examples/rtdl_dbscan_clustering_app.py \
  --backend optix --copies 1024 \
  --optix-summary-mode rt_core_flags_prepared \
  --output-mode core_count
```

## Boundary

These are bounded fixed-radius threshold-decision/count paths only. They do not
claim neighbor-row materialization speedup, complete DBSCAN clustering, broad
spatial analytics speedup, or any public NVIDIA performance wording.
