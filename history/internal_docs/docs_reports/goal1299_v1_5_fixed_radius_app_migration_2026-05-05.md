# Goal1299: Fixed-Radius App Migration To Generic Primitive

Date: 2026-05-05

## Purpose

Goal1299 migrates two small prepared fixed-radius app paths onto the Goal1298
generic primitive wrapper:

- `examples/rtdl_service_coverage_gaps.py`
- `examples/rtdl_event_hotspot_screening.py`

This is an internal v1.5 migration slice. It does not change app claim
boundaries or authorize public speedup wording.

## Change

`service_coverage_gaps` now routes:

- Embree `gap_summary` through `run_generic_fixed_radius_count_threshold_2d(...)`
- OptiX `gap_summary_prepared` through
  `run_generic_prepared_fixed_radius_threshold_reached_count_2d(...)`

`event_hotspot_screening` now routes:

- Embree `count_summary` through `run_generic_fixed_radius_count_threshold_2d(...)`
- OptiX `count_summary_prepared` through
  `run_generic_prepared_fixed_radius_threshold_reached_count_2d(...)`

The app payloads preserve existing summary outputs and native-continuation
metadata.

## Local Verification

Passed locally:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1299_v1_5_fixed_radius_app_migration_test \
  tests.goal810_spatial_apps_optix_summary_surface_test \
  tests.goal955_spatial_prepared_native_continuation_test \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test
```

Result: 19 tests OK.

Passed locally:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_service_coverage_gaps.py \
  examples/rtdl_event_hotspot_screening.py \
  tests/goal1299_v1_5_fixed_radius_app_migration_test.py
```

`git diff --check` passed.

## Next Pod Action

Run the migrated OptiX summary paths on the active RTX pod:

```text
PYTHONPATH=src:. python3 examples/rtdl_service_coverage_gaps.py \
  --backend optix --copies 1024 \
  --optix-summary-mode gap_summary_prepared --require-rt-core

PYTHONPATH=src:. python3 examples/rtdl_event_hotspot_screening.py \
  --backend optix --copies 1024 \
  --optix-summary-mode count_summary_prepared --require-rt-core
```

## Boundary

These are bounded fixed-radius threshold-count app paths only. They do not
claim whole-app acceleration, row materialization acceleration, clinic-load
calculation, hotspot-id materialization, ANN, DBSCAN, Hausdorff, Barnes-Hut, or
public NVIDIA speedup performance.
