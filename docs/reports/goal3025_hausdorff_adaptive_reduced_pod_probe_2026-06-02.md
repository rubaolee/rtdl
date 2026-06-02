# Goal3025: Hausdorff Adaptive-Reduced OptiX Pod Probe

Date: 2026-06-02

## Purpose

Goal3025 tested whether the exact 2D Hausdorff OptiX path could get faster by
composing existing generic point-group primitives into an adaptive-reduced path:

- `threshold_flags`
- `nearest_max_distance_row`
- prepared point-group nearest-witness handles

The intent was to avoid materializing full witness rows and avoid a Python row
loop while keeping the native engine app-agnostic.

No native Hausdorff-specific ABI or kernel was added.

## Pod Environment

- GPU: `NVIDIA L4, 565.57.01`
- CUDA toolchain used for OptiX PTX: `/usr/local/cuda-12.6`
- Source commit: `f0f0253f1fa928ff3a4ba4929ebdf0eb77913c45`
- Dirty source list: empty

The pod artifact is stored at:

- `docs/reports/goal3025_hausdorff_adaptive_reduced_pod_probe_2026-06-02.json`

## Results

| Points | Method | Exact | RT-backed | Wall seconds | CuPy grouped-grid seconds | Ratio vs CuPy | Threshold iterations |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |
| 512 | `rtdl_rt_grouped_adaptive_reduced_nearest_witness` | yes | yes | 1.3788113221526146 | 0.000703670084476471 | 1959.457070252528x | 2 |
| 4096 | `rtdl_rt_grouped_adaptive_reduced_nearest_witness` | yes | yes | 1.2940954267978668 | 0.0037913545966148376 | 341.3279855050534x | 4 |

The correctness check passed for both rows: the RTDL/OptiX result matched the
CuPy grouped-grid comparison path.

## Finding

The adaptive-reduced path is correct, but it is not a performance improvement.
At 4096 points, the best current RT path from Goal3024 remains the older
adaptive row path with target group size 512:

- `rtdl_rt_grouped_adaptive_nearest_witness_target_group_512`
- `0.7740153260529041` seconds at 4096 points

The new adaptive-reduced method took `1.2940954267978668` seconds at the same
4096-point shape. The likely reason is that the path trades Python row
materialization for host flag copies plus additional native reduction calls.
That is the wrong trade at this scale.

## Decision

Do not promote `rtdl_rt_grouped_adaptive_reduced_nearest_witness` as the
recommended exact Hausdorff RT path.

This is useful negative design evidence. The next serious RT Hausdorff attempt
should not be another host-orchestrated sequence of threshold flags and native
reductions. It should be a generic device-resident active-set compaction /
candidate-frontier / nearest-witness continuation that keeps more of the
worklist and reduction state on the device.

## Boundaries

This report does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- whole-app speedup wording
- true zero-copy wording
- package-install claims
- app-specific native-engine behavior

The native engine boundary remains app-agnostic: points, groups, thresholds,
nearest witnesses, and max-distance reductions are generic primitives; Hausdorff
semantics remain in the Python benchmark application.
