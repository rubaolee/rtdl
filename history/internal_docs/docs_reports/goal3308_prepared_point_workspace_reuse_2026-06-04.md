# Goal3308 Prepared Point-Probe Workspace Reuse

Date: 2026-06-04

Status: complete with RTX A5000 pod evidence; small additional repeated-query
win, gap remains.

## Purpose

Goal3306 moved query point upload out of the repeated scalar-count timed lane.
The next remaining per-call overhead was native workspace allocation: the
prepared-points count path still allocated a device count buffer and launch
parameter buffer on every call.

Goal3308 moves those two generic device buffers into the reusable prepared
point-probe handle:

- `PreparedPointProbeColumns2D::d_count`
- `PreparedPointProbeColumns2D::d_params`

The count call still resets and uploads the count and launch parameters each
launch, but it no longer allocates those buffers per call.

## Implementation

Changed only the generic prepared point-probe path in
`src/native/optix/rtdl_optix_workloads.cpp`. No RayJoin-specific native logic
was added.

The existing Python/API surface from Goal3306 remains unchanged:

`device_filtered_prepared_points_validated`

The benchmark app still validates each timed device-filtered count against the
exact prepared count and preserves inclusive boundary semantics.

## Validation

Local:

- `tests.goal3306_prepared_point_probe_columns_scalar_count_test`: 4 tests passed

Pod:

- GPU: NVIDIA RTX A5000, driver 580.126.09
- RTDL commit: `8d8e7c02986df235f5b0719ade521465bbcb0a05`
- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk`
- `tests.goal3306_prepared_point_probe_columns_scalar_count_test`: 4 tests passed

Artifact:

- `docs/reports/goal3308_workspace_reuse_prepared_points_rayjoin_same_slice_pod_2026-06-04.json`

## Timing

| packet | RayJoin PIP query median | RTDL PIP prepared-query median | RTDL / RayJoin | RTDL count |
| --- | ---: | ---: | ---: | ---: |
| Goal3306 same-commit baseline, old mode | 0.221 ms | 0.343 ms | 1.56x | 1430 |
| Goal3306 prepared point columns | 0.222 ms | 0.317 ms | 1.43x | 1430 |
| Goal3308 prepared point columns + workspace reuse | 0.220 ms | 0.303 ms | 1.38x | 1430 |

Native phase medians for Goal3308 PIP:

- native count pass: about 0.262 ms;
- point upload inside timed lane: 0.000 ms;
- point pack inside timed lane: 0.000 ms;
- prepared point-column setup outside timed lane: about 0.036 ms.

## Interpretation

Workspace reuse is a small but real overhead improvement on top of Goal3306:

- Goal3306 prepared-points median: 0.317 ms;
- Goal3308 prepared-points + reusable workspace median: 0.303 ms.

The current best RTDL RayJoin PIP route is therefore:

`device_filtered_prepared_points_validated + inclusive + z_point + scalar count pipeline`

This still does not beat RayJoin. The remaining gap is now dominated by the
generic native count/traversal pass around 0.26 ms. Further progress likely
requires batched/replayed scalar-count launches or a more compact generic
closed-shape predicate-count path. Another per-call allocation tweak is unlikely
to close the gap by itself.

## Boundary

This packet does not authorize:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims.

The native engine remains app-agnostic.
