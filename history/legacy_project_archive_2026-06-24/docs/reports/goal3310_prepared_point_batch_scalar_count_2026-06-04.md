# Goal3310 Prepared Point Batch Scalar Count

Date: 2026-06-04

Status: complete with RTX A5000 pod evidence; repeated-query throughput improves
modestly, one-shot RayJoin gap remains.

## Purpose

Goal3308 showed that per-call allocation reuse helped, but the remaining
closed-shape PIP count lane was dominated by the synchronous native scalar-count
pass. Goal3310 adds a generic batch count surface for repeated prepared
point-probe requests:

`rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_2d`

The Python method is:

`PreparedOptixPointClosedShapeMembership2D.count_device_filtered_prepared_points_batch(...)`

The primitive takes one prepared closed-shape scene, one prepared point-probe
column handle, a `request_count`, and returns one count per request. Internally
it queues repeated OptiX scalar-count launches on one stream and synchronizes
once. It does not add RayJoin-specific native logic.

## Validation

Local:

- `tests.goal3310_prepared_point_batch_scalar_count_test`: 4 tests passed
- `tests.goal3308_prepared_point_workspace_reuse_test`: 2 tests passed
- `tests.goal3306_prepared_point_probe_columns_scalar_count_test`: 4 tests passed
- `py_compile` passed for `scripts/goal3310_rayjoin_pip_batch_scalar_count_probe.py`
  and `src/rtdsl/optix_runtime.py`

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- RTDL commit: `7181367f7a772d1fcff60f9378ea90824297ea63`
- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`: passed
- `tests.goal3310_prepared_point_batch_scalar_count_test`: 4 tests passed
- live smoke: exact count `2`, single count `2`, batch counts `[2, 2, 2, 2, 2]`,
  phase mode `prepared_points_device_filtered_batch_count`

Artifact:

- `docs/reports/goal3310_rayjoin_pip_batch_probe_2026-06-04.json`

## RayJoin Slice Probe

Dataset:

`/root/rtdl_goal3293/data/rayjoin_public_cdb/br_county_start0_count512.cdb`

Probe shape:

- 512 point probes
- 481 closed shapes
- query axis: `z_point`
- boundary mode: `inclusive`
- scalar count pipeline enabled
- exact validation count: `1430`

| request count | total median ms | per-request median ms | native per-request median ms | count |
| ---: | ---: | ---: | ---: | ---: |
| single method | 0.280 | 0.280 | n/a | 1430 |
| 1 | 0.286 | 0.286 | 0.262 | 1430 |
| 2 | 0.527 | 0.264 | 0.251 | 1430 |
| 4 | 1.006 | 0.251 | 0.245 | 1430 |
| 8 | 1.974 | 0.247 | 0.243 | 1430 |
| 16 | 3.898 | 0.244 | 0.242 | 1430 |
| 32 | 7.759 | 0.242 | 0.241 | 1430 |

The best repeated-query per-request result is about `0.242 ms`, versus about
`0.280 ms` for the direct single-call method in the same probe. That is about a
`1.16x` throughput improvement for this repeated-query lane.

## Interpretation

This result is useful, but it is not a RayJoin-beating result.

The batch API removes some per-request host/synchronization overhead, but the
per-request floor quickly approaches the native scalar-count traversal work
itself. On this slice the native per-request time settles near `0.241 ms`.

This means the next meaningful performance improvement cannot come from another
small host-allocation tweak. It likely requires one of:

- a more compact generic closed-shape predicate-count path;
- CUDA graph replay or a true replayable launch object if OptiX capture is
  reliable for this pipeline;
- a deeper generic primitive that evaluates more of the closed-shape predicate
  per launch without changing app semantics.

## Boundary

This packet does not authorize:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims.

Batch rows are repeated-query throughput evidence only. They do not replace
one-shot RayJoin latency comparisons.
