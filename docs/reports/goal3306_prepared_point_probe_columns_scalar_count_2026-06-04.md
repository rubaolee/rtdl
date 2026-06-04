# Goal3306 Prepared Point-Probe Columns For Scalar Count

Date: 2026-06-04

Status: complete with RTX A5000 pod evidence; modest repeated-query win, gap
remains.

## Purpose

Goal3305 accepted the RayJoin count-tuning chain and agreed that the next useful
target was generic scalar-count launch/packing/residency overhead. Goal3306
adds that narrow primitive:

- prepare generic 2-D point-probe columns once on the OptiX device;
- reuse those columns in the generic prepared point/closed-shape
  device-filtered scalar-count path;
- keep exact validation and inclusive boundary semantics unchanged in the
  RayJoin benchmark app.

This is not a RayJoin-specific native path. RayJoin only opts into a generic
prepared point-probe-column front door.

## Implementation

New native exports:

- `rtdl_optix_prepare_point_probe_columns_2d`
- `rtdl_optix_count_prepared_point_closed_shape_membership_device_filtered_prepared_points_2d`
- `rtdl_optix_destroy_prepared_point_probe_columns_2d`

New Python runtime surface:

- `PreparedOptixPointProbeColumns2D`
- `prepare_point_probe_columns_2d_optix(...)`
- `PreparedOptixPointClosedShapeMembership2D.prepare_point_probe_columns(...)`
- `PreparedOptixPointClosedShapeMembership2D.count_device_filtered_prepared_points(...)`

New RayJoin benchmark count mode:

`device_filtered_prepared_points_validated`

The app still validates every timed sample against exact prepared count before
accepting the device-filtered count. The timed lane uses prepared point columns;
the point-column preparation is reported separately as
`prepare_query_points_ms`.

## Validation

Local focused tests:

- `tests.goal3306_prepared_point_probe_columns_scalar_count_test`
- `tests.goal3244_rayjoin_same_slice_repeated_count_runner_test`
- `tests.goal3304_current_best_rayjoin_same_slice_test`
- `tests.goal3303_rayjoin_scalar_count_negative_tuning_probes_test`
- `tests.goal3300_rayjoin_boundary_event_count_route_test`

Result: 28 tests passed.

Pod validation:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- RTDL commit: `7890701c9d70dffc4a281d0a4ff5f207606859d2`
- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- `tests.goal3306_prepared_point_probe_columns_scalar_count_test`: 3 tests passed

Artifacts:

- `docs/reports/goal3306_prepared_points_rayjoin_same_slice_pod_2026-06-04.json`
- `docs/reports/goal3306_baseline_device_filtered_same_slice_pod_2026-06-04.json`

## Same-Commit Pod Timing

Both rows below ran at commit `7890701c9d70dffc4a281d0a4ff5f207606859d2` on the
same A5000 pod with 4 RTDL warmups and 20 RTDL repeats. RayJoin query timing is
the unpatched upstream `query_exec` reported median, as in Goal3244.

| mode | RayJoin PIP query median | RTDL PIP prepared-query median | RTDL / RayJoin | RTDL count |
| --- | ---: | ---: | ---: | ---: |
| `device_filtered_validated` | 0.221 ms | 0.343 ms | 1.56x | 1430 |
| `device_filtered_prepared_points_validated` | 0.222 ms | 0.317 ms | 1.43x | 1430 |

The prepared-points route reduces RTDL PIP prepared-query median by about
0.026 ms, or 7.7% relative to the same-commit baseline. It also improves the
RayJoin ratio from 1.56x to 1.43x on this slice.

Native phase medians:

| mode | native count pass | point upload inside timed lane | point pack inside timed lane | prepared point-column setup |
| --- | ---: | ---: | ---: | ---: |
| `device_filtered_validated` | 0.261 ms | 0.020 ms | 0.001 ms | n/a |
| `device_filtered_prepared_points_validated` | 0.261 ms | 0.000 ms | 0.000 ms | 0.035 ms |

## Interpretation

This is a real repeated-query overhead improvement. It is useful when the caller
can prepare the same query points once and run repeated scalar counts against a
prepared closed-shape scene.

It is not a one-shot improvement. If point-column preparation is charged to a
single query, the prepared-points route adds about 0.035 ms up front and would
not beat the old one-call path. That is acceptable: the benchmark contract here
is repeated same-slice query timing, matching the RayJoin query loop style.

The remaining bottleneck is not point upload. The native count pass remains
about 0.261 ms in both modes. The next useful target is a deeper generic
scalar-count overhead reduction: persistent launch parameter/count buffers,
batched/replayed scalar count launches, or a more compact generic
closed-shape predicate-count path. It should not relax inclusive boundary
semantics or reintroduce app-specific native logic.

## Boundary

This packet does not authorize:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims.

The native engine remains app-agnostic. The new primitive is generic
point-probe-column preparation plus generic point/closed-shape scalar count.
