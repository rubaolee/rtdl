# Goal 803 RT-Core App Maturity Contract

Date: 2026-04-23

Status: implemented locally

## Purpose

This goal codifies the next development direction:

Every general public RTDL app should eventually either:

- honestly reach a NVIDIA RT-core-backed OptiX traversal status for its
  RTDL-owned acceleration slice; or
- be explicitly kept out of NVIDIA RT-core app claims until that redesign is
  done.

This is also a cloud-cost contract: we do not restart paid pods per app. Local
implementation, correctness tests, docs, manifests, and review packets happen
first; then all eligible paths are validated in one batched cloud session.

## Machine-Readable API

Added:

- `rtdsl.rt_core_app_maturity(app)`
- `rtdsl.rt_core_app_maturity_matrix()`
- `rtdsl.RT_CORE_APP_MATURITY_STATUSES`

Statuses:

- `rt_core_ready`
- `rt_core_partial_ready`
- `needs_rt_core_redesign`
- `needs_optix_app_surface`
- `not_nvidia_rt_core_target`

## Current Contract Summary

Currently `rt_core_ready`:

- `outlier_detection`
- `dbscan_clustering`
- `robot_collision_screening`

Currently `rt_core_partial_ready`:

- `database_analytics`

Needs RT-core redesign:

- `graph_analytics`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `hausdorff_distance`
- `ann_candidate_search`
- `barnes_hut_force_app`

Needs an OptiX app surface plus true RT traversal design:

- `service_coverage_gaps`
- `event_hotspot_screening`
- `facility_knn_assignment`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Not NVIDIA RT-core targets:

- `apple_rt_demo`
- `hiprt_ray_triangle_hitcount`

## Files Changed

- `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/tests/goal803_rt_core_app_maturity_contract_test.py`

## Verification

Run:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest -v tests.goal803_rt_core_app_maturity_contract_test
```

Expected:

- every public app has a maturity row;
- only the three prepared scalar/pose-count paths are currently `rt_core_ready`;
- every non-engine-specific app targets `rt_core_ready`;
- cloud policies do not permit per-app pod restart cycles;
- public docs record the contract.

## Release Boundary

This goal does not make any new app RT-core accelerated. It creates the
contract and gating API for the work.

Allowed statement:

- RTDL now has a machine-readable v1.0 RT-core app maturity contract.

Disallowed statement:

- all apps already use NVIDIA RT cores.

## Next Step

Start implementation by priority:

1. Keep and harden ready paths: robot, outlier, DBSCAN.
2. Move DB from `rt_core_partial_ready` to `rt_core_ready`.
3. Redesign segment/polygon and road-hazard around a native compact OptiX path.
4. Decide whether graph gets a real RT lowering or exits NVIDIA RT-core targets.
5. Redesign Hausdorff, ANN, and Barnes-Hut only if a true traversal mapping is
   credible; otherwise keep them as GPU-compute/app examples, not RT-core apps.
