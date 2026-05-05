# Goal1302: Barnes-Hut And Hausdorff Generic Fixed-Radius Migration

Date: 2026-05-05

## Purpose

Goal1302 migrates two remaining fixed-radius prepared OptiX decision paths onto
the Goal1298 generic scalar threshold-count primitive:

- `barnes_hut_force_app / node_coverage_prepared`
- `hausdorff_distance / directed_threshold_prepared`

This is an internal v1.5 migration slice. It does not claim Barnes-Hut force
reduction, Hausdorff distance computation, whole-app acceleration, or public
NVIDIA speedup.

## Change

Both paths now call:

```text
run_generic_prepared_fixed_radius_threshold_reached_count_2d(...)
```

The existing app CLI modes and payload boundaries are preserved. App payloads
now expose:

```text
generic_primitive = FIXED_RADIUS_COUNT_THRESHOLD_2D
summary_primitive = REDUCE_INT(COUNT)
```

## Local Verification

Passed locally:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal882_barnes_hut_node_coverage_optix_subpath_test \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test
```

Result:

```text
Ran 21 tests in 0.031s

OK
```

Passed locally:

```text
PYTHONPATH=src:. python3 -m py_compile \
  examples/rtdl_barnes_hut_force_app.py \
  examples/rtdl_hausdorff_distance_app.py \
  tests/goal882_barnes_hut_node_coverage_optix_subpath_test.py \
  tests/goal879_hausdorff_threshold_rt_core_subpath_test.py \
  tests/goal957_graph_hausdorff_native_continuation_metadata_test.py
```

`git diff --check` passed.

## Next Pod Action

Run the migrated OptiX prepared decision paths on the active RTX pod:

```text
PYTHONPATH=src:. python3 examples/rtdl_barnes_hut_force_app.py \
  --backend optix --body-count 4096 \
  --optix-summary-mode node_coverage_prepared --require-rt-core

PYTHONPATH=src:. python3 examples/rtdl_hausdorff_distance_app.py \
  --backend optix --copies 1024 \
  --optix-summary-mode directed_threshold_prepared \
  --hausdorff-threshold 0.4 --require-rt-core
```

## Boundary

These are bounded fixed-radius threshold decisions only. They do not claim
Barnes-Hut opening-rule evaluation, force-vector reduction, exact Hausdorff
distance, nearest-neighbor row speedup, whole-app acceleration, or public
NVIDIA speedup wording.
