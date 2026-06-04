# Goal3312 Prepared Point Batch Graph Negative Probe

Date: 2026-06-04

Status: complete as a fail-closed negative probe; not accepted as a performance
optimization.

## Purpose

Goal3310 showed that batching prepared point/closed-shape scalar counts improves
repeated-query throughput modestly but still leaves the native traversal/count
floor near `0.241 ms` per request on the A5000 RayJoin PIP slice.

Goal3312 tested the next obvious host-overhead lever: capture a fixed prepared
batch-count sequence as a CUDA graph and replay it as one launch object.

## Implementation

Added a generic graph handle:

`PreparedPointClosedShapeMembershipPreparedPointsBatchGraph2D`

Native C ABI:

- `rtdl_optix_prepare_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d`
- `rtdl_optix_replay_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d`
- `rtdl_optix_destroy_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_graph_2d`

Python wrapper:

- `PreparedOptixPointClosedShapeBatchCountGraph2D`
- `PreparedOptixPointClosedShapeMembership2D.prepare_device_filtered_prepared_points_batch_graph(...)`

The Python wrapper validates graph replay against the trusted batch-count path
before returning a graph handle. If replay disagrees, it closes the native graph
and raises.

## Validation

Local:

- `tests.goal3312_prepared_point_batch_graph_count_test`: 3 tests passed
- `tests.goal3310_prepared_point_batch_scalar_count_test`: 5 tests passed
- `py_compile` passed for `src/rtdsl/optix_runtime.py` and `src/rtdsl/__init__.py`

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- RTDL commit: `5970995b1b858f75af57da16f03dba0ce07f6d4b`
- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`: passed
- `tests.goal3312_prepared_point_batch_graph_count_test`: 3 tests passed
- `tests.goal3310_prepared_point_batch_scalar_count_test`: 5 tests passed

Artifact:

- `docs/reports/goal3312_batch_graph_replay_negative_probe_2026-06-04.json`

## Result

Small live smoke:

- exact count: `2`
- trusted single prepared count: `2`
- trusted batch count: `[2, 2, 2, 2, 2]`
- graph replay observed: `[0, 0, 0, 0, 0]`
- wrapper status: `failed_closed`

Error:

`prepared OptiX batch-count graph replay failed validation: (0, 0, 0, 0, 0) != (2, 2, 2, 2, 2)`

The graph telemetry mode was:

`prepared_points_device_filtered_batch_graph_replay`

## Interpretation

This path is not currently usable as a performance optimization. CUDA graph
capture/replay of this OptiX scalar-count launch sequence did not produce
correct counts on the A5000 pod.

The important engineering result is that the public Python wrapper fails closed
instead of returning incorrect graph replay counts. Future work should not use
this graph path for performance evidence until the native replay mismatch is
understood and fixed.

The next useful direction remains a more compact generic closed-shape
predicate-count primitive, not an accepted CUDA-graph replay claim.

## Boundary

This packet does not authorize:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims.

This is negative evidence plus a fail-closed guard, not a performance win.
