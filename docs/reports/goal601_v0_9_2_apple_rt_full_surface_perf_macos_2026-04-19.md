# Goal601: Apple RT Full-Surface Performance Characterization

Date: 2026-04-19

Status: characterization artifact

## Methodology

- Warmups before sample window: `5`
- Measured repeats: `20`
- Stability threshold: coefficient of variation <= `0.3`
- Embree is the mature local RTDL baseline.
- `native_mps_rt` rows are Apple Metal/MPS RT native slices.
- `cpu_reference_compat` rows are callable through `run_apple_rt`, but they are not Apple hardware-backed RT execution.

## Host

```json
{
  "platform": "macOS-26.3-arm64-arm-64bit-Mach-O",
  "machine": "arm64",
  "processor": "arm"
}
```

## Versions

```json
{
  "apple_rt": [
    0,
    9,
    2
  ],
  "apple_rt_context": "Apple M4",
  "embree": [
    4,
    4,
    0
  ]
}
```

## Results

This table has 19 measured shape rows for the 18-predicate Apple RT surface because `ray_triangle_hit_count` has both a 2D compatibility shape and a 3D native Apple RT shape.

| Workload | Apple mode | Rows | Embree median | Apple RT median | Apple/Embree | Parity | Stable |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `segment_intersection_2d` | `native_mps_rt` | 4 | 0.000013729 s | 0.001051750 s | 76.608x | True | False |
| `point_in_polygon` | `cpu_reference_compat` | 2 | 0.000012458 s | 0.000010542 s | 0.846x | True | True |
| `overlay_compose` | `cpu_reference_compat` | 1 | 0.000016375 s | 0.000019979 s | 1.220x | True | True |
| `ray_triangle_hit_count_2d` | `cpu_reference_compat` | 1 | 0.000015105 s | 0.000010583 s | 0.701x | True | True |
| `ray_triangle_hit_count_3d` | `native_mps_rt` | 32 | 0.000115396 s | 0.021272083 s | 184.339x | True | True |
| `ray_triangle_closest_hit_3d` | `native_mps_rt` | 1 | 0.000020334 s | 0.000618355 s | 30.411x | True | False |
| `segment_polygon_hitcount` | `cpu_reference_compat` | 1 | 0.000017666 s | 0.000024125 s | 1.366x | True | True |
| `segment_polygon_anyhit_rows` | `cpu_reference_compat` | 1 | 0.000017708 s | 0.000024000 s | 1.355x | True | True |
| `polygon_pair_overlap_area_rows` | `cpu_reference_compat` | 1 | 0.000019709 s | 0.000035250 s | 1.789x | True | True |
| `polygon_set_jaccard` | `cpu_reference_compat` | 1 | 0.000018437 s | 0.000030125 s | 1.634x | True | True |
| `point_nearest_segment` | `cpu_reference_compat` | 1 | 0.000013271 s | 0.000008896 s | 0.670x | True | True |
| `fixed_radius_neighbors` | `cpu_reference_compat` | 1 | 0.000018854 s | 0.000009417 s | 0.499x | True | False |
| `knn_rows` | `cpu_reference_compat` | 2 | 0.000019167 s | 0.000009959 s | 0.520x | True | True |
| `bounded_knn_rows` | `cpu_reference_compat` | 1 | 0.000022125 s | 0.000009896 s | 0.447x | True | False |
| `bfs_discover` | `cpu_reference_compat` | 2 | 0.000022979 s | 0.000011355 s | 0.494x | True | True |
| `triangle_match` | `cpu_reference_compat` | 1 | 0.000021438 s | 0.000009458 s | 0.441x | True | False |
| `conjunctive_scan` | `cpu_reference_compat` | 2 | 0.000041271 s | 0.000012333 s | 0.299x | True | True |
| `grouped_count` | `cpu_reference_compat` | 2 | 0.000043521 s | 0.000013292 s | 0.305x | True | True |
| `grouped_sum` | `cpu_reference_compat` | 2 | 0.000044146 s | 0.000014042 s | 0.318x | True | False |

## Interpretation

This report answers the full-surface question. The current Apple RT API can run the measured workload surface, but only the rows marked `native_mps_rt` are Apple Metal/MPS RT native execution.

The compatibility rows are useful for API uniformity and app portability, but they must not be used as Apple RT hardware-speed evidence.

The tiny native rows in this full-surface table are overhead-characterization fixtures. They are intentionally small so every supported shape can be measured quickly in one report. For native Apple RT performance wording, use the scaled Goal600 artifact:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal600_v0_9_2_pre_release_apple_rt_perf_macos_2026-04-19.md`

Combining both artifacts gives the current honest answer:

- Full API surface: callable through `run_apple_rt`, with parity on all measured rows.
- Native Apple RT surface: 3D closest-hit, 3D hit-count, and 2D segment-intersection.
- Performance: closest-hit is the strongest current native Apple RT result on this Mac; hit-count and segment-intersection are correct but still not performance-leading versus Embree.
