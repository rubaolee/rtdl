# Goal3686 Resident Native Scalar-Count Executor

Date: 2026-06-07

## Purpose

Goal3684 moved dense-boundary exact closed-shape scalar count from a Numba boundary-row continuation into a generic native OptiX scalar-correction path. That removed dense boundary-row materialization, but the one-shot native method still allocated temporary native counters and launch parameters on each call.

Goal3686 adds a reusable native scalar-count executor for repeated prepared workloads.

The executor stays generic:

- prepared point/closed-shape membership,
- relation status,
- exact boundary correction,
- scalar count,
- reusable native executor.

It does not introduce RayJoin, CDB, county, GIS, overlay, or app-specific ABI names.

## Implementation

Changed files:

- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py`
- `tests/goal3686_resident_native_scalar_count_executor_test.py`

New native symbols:

- `rtdl_optix_prepare_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d`
- `rtdl_optix_run_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d`
- `rtdl_optix_destroy_point_closed_shape_membership_relation_status_corrected_scalar_count_executor_2d`

Python front door:

`PreparedOptixPointClosedShapeMembership2D.prepare_relation_status_corrected_scalar_count_executor(...)`

The executor owns reusable native buffers for:

- exact count,
- all accepted relation candidate count,
- boundary candidate count,
- dropped boundary candidate count,
- launch parameters.

Each run resets counters, uploads the launch parameters, launches the generic OptiX scalar-correction pipeline, synchronizes, and downloads only scalar counters.

## A5000 Evidence

Artifact:

`docs/reports/goal3686_resident_native_scalar_count_executor_a5000/summary.json`

Source commit:

`e7f7ca88`, with `goal3677_scoped_source_dirty=false`

Dataset:

`data/rayjoin_public_cdb/br_county_start0_count16545.cdb`

Rows:

- points: `16545`
- shapes: `15700`
- exact oracle count: `47262`

Hot medians:

| Route | Median seconds | Stable count |
| --- | ---: | ---: |
| all relation candidates, count-only | `0.000460814` | `47264` |
| boundary-status candidate columns | `0.003911417` | `47241` |
| relation-status corrected exact Numba count | `0.003182082` | `47262` |
| resident relation-status corrected exact Numba count | `0.001813552` | `47262` |
| native relation-status corrected exact scalar count | `0.000510537` | `47262` |
| resident native relation-status corrected exact scalar count | `0.000474052` | `47262` |

Correctness:

- resident native corrected count: `47262`
- exact oracle count: `47262`
- resident native all-match exact count: `true`

Relative to the resident Numba corrected path in the same packet, the resident native executor is about `3.83x` faster (`0.001813552 / 0.000474052`). Relative to the one-shot native scalar path, it is about `1.08x` faster (`0.000510537 / 0.000474052`).

## Interpretation

The main win was Goal3684's removal of dense boundary-row materialization. Goal3686 is a smaller but useful resident-workload hardening step:

- it preserves the same exact scalar result,
- it avoids per-run native counter/parameter allocation,
- it keeps repeated runs below the all-candidate count-only path plus correction overhead,
- it remains a generic engine primitive rather than an app-specific optimization.

The boundary-status candidate-column route appeared slower in this packet than in the Goal3684 packet. That row is retained only as a diagnostic comparison; it is no longer the preferred scalar-count route because the resident native executor avoids producing the dense boundary stream entirely.

## Boundary

This report does not authorize:

- release,
- default-route promotion,
- public speedup claims,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- broad RT-core speedup claims,
- true zero-copy claims.

The evidence authorizes only this internal engineering conclusion: the reusable generic native scalar-count executor is exact on the measured full public county dataset and reduces repeated-run overhead versus the one-shot native scalar path while avoiding dense boundary-row materialization.

## Next Work

Recommended next steps:

1. external review of Goals3684 and 3686 together,
2. decide whether this executor should become the recommended RayJoin count reference route,
3. test whether this executor pattern helps other dense-boundary scalar benchmark rows,
4. keep partner/user-choice docs clear that this is a built-in primitive path, not an app-specific native engine customization.
