# Goal1298: Generic Fixed-Radius Threshold-Count Primitive

Date: 2026-05-05

## Purpose

Goal1298 adds an app-name-free v1.5 wrapper for the fixed-radius
count-threshold primitive used by several prepared OptiX app paths.

The point is to move from app-specific calls like
`prepare_optix_fixed_radius_count_threshold_2d(...)` toward a generic primitive
surface that apps can migrate to:

- direct 2-D fixed-radius count-threshold rows;
- reusable prepared 2-D fixed-radius count-threshold scenes;
- scalar `threshold_reached_count` reduction using `REDUCE_INT(COUNT)`;
- active backends limited to CPU/Embree/OptiX;
- frozen-backend rejection for Vulkan/HIPRT/Apple RT before v2.1.

## Added API

- `run_generic_fixed_radius_count_threshold_2d(...)`
- `prepare_generic_fixed_radius_count_threshold_2d(...)`
- `run_generic_prepared_fixed_radius_threshold_reached_count_2d(...)`
- `GenericPreparedFixedRadiusCountThreshold2D`

## Boundary

This is not a new app claim. It is the generic primitive boundary beneath
existing app-shaped paths such as ANN candidate coverage, DBSCAN core flags,
coverage summaries, Hausdorff threshold decisions, and Barnes-Hut node coverage.

No public speedup wording is authorized by this goal.

## Local Verification

Passed locally:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_count_test \
  tests.goal1298_v1_5_generic_fixed_radius_threshold_evidence_test \
  tests.goal1295_v1_5_generic_prepared_scene_session_test \
  tests.goal1297_v1_5_graph_visibility_reusable_scene_batches_test
```

Result: 17 tests OK.

Passed locally:

```text
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/generic_primitives.py \
  scripts/goal1298_v1_5_generic_fixed_radius_threshold_evidence.py \
  tests/goal1298_v1_5_generic_fixed_radius_threshold_count_test.py \
  tests/goal1298_v1_5_generic_fixed_radius_threshold_evidence_test.py
```

`git diff --check` passed.

## Next Pod Action

Run:

```text
PYTHONPATH=src:. python3 scripts/goal1298_v1_5_generic_fixed_radius_threshold_evidence.py \
  --copies 1024 \
  --backends cpu embree optix \
  --output docs/reports/goal1298_v1_5_generic_fixed_radius_threshold_pod_results/evidence.json
```
