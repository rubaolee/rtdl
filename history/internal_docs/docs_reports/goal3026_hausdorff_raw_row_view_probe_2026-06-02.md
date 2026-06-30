# Goal3026: Hausdorff Raw Row-View OptiX Probe

Date: 2026-06-02

## Purpose

Goal3026 tested a current-basis improvement for the exact 2D Hausdorff
RTDL/OptiX path: expose prepared point-group nearest-witness results as a
generic `OptixRowView`, then let the benchmark application consume
`rows_ptr` directly instead of materializing Python dictionaries.

This keeps the native engine app-agnostic. The native ABI remains the generic
point-group nearest-witness endpoint:

- `rtdl_optix_run_prepared_point_group_nearest_witness_2d`

No native Hausdorff-specific ABI or kernel was added.

## Pod Environment

- GPU: `NVIDIA L4, 565.57.01`
- CUDA toolchain used for OptiX PTX: `/usr/local/cuda-12.6`
- Source commit: `38b2d88ece9e9eedf0efe19624dec2f710a8ae64`
- Dirty source list: empty
- Warmup: 1
- Repeats per row: 3

The pod artifact is stored at:

- `docs/reports/goal3026_hausdorff_raw_row_view_probe_2026-06-02.json`

## Results

| Points | Method | Median seconds | RT-backed | Exact | Notes |
| ---: | --- | ---: | --- | --- | --- |
| 512 | `rtdl_rt_grouped_adaptive_nearest_witness` | 0.007991146296262741 | yes | yes | old adaptive row path |
| 512 | `rtdl_rt_grouped_adaptive_raw_nearest_witness` | 0.0067427754402160645 | yes | yes | raw row-view path |
| 512 | `cupy_grouped_grid_rawkernel` | 0.0007095299661159515 | no | yes | dense CUDA-core partner reference |
| 4096 | `rtdl_rt_grouped_adaptive_nearest_witness` | 0.07598104327917099 | yes | yes | old adaptive row path |
| 4096 | `rtdl_rt_grouped_adaptive_raw_nearest_witness` | 0.053286220878362656 | yes | yes | raw row-view path |
| 4096 | `cupy_grouped_grid_rawkernel` | 0.00373150035738945 | no | yes | dense CUDA-core partner reference |

The raw row-view path preserved exact distances and witnesses:

- 512 points: distance `0.14627873169442843`, witness `447 -> 486`
- 4096 points: distance `0.13528455701336056`, witness `472 -> 1183`

## Interpretation

The raw row-view path is a real current-basis RT improvement:

- 512 points: `0.8437807531279325x` raw/old adaptive ratio
- 4096 points: `0.7013094132253148x` raw/old adaptive ratio

So `rtdl_rt_grouped_adaptive_raw_nearest_witness` should replace `rtdl_rt_grouped_adaptive_nearest_witness` as the preferred current exact RTDL/OptiX adaptive Hausdorff method.

However, it does not close the dense exact Hausdorff performance gap:

- 512 points: raw RT is `9.503158093697989x` slower than CuPy grouped-grid
- 4096 points: raw RT is `14.280106063192658x` slower than CuPy grouped-grid

The design lesson is precise. Removing Python dictionary materialization helps,
but the remaining gap still points to device-resident active-set compaction,
candidate-frontier construction, and nearest-witness continuation. The next RT
leap should be generic runtime/primitive work, not an app-specific Hausdorff
native engine path.

## Boundaries

This report does not authorize:

- v2.6 release
- public speedup wording
- broad RT-core speedup wording
- whole-app speedup wording
- true zero-copy wording
- package-install claims
- app-specific native-engine behavior

The result is internal optimization evidence for one benchmark-app path on one
L4 pod. It is not a claim that RTDL beats CuPy, X-HD, or every CUDA-core
implementation for exact dense Hausdorff distance.
