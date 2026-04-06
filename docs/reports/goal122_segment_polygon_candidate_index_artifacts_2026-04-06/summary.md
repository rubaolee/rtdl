# Goal 122 Candidate-Index Linux Large-Scale Performance Artifact

- Generated: `2026-04-06T12:13:10`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `(0, 1, 0)`, embree `(4, 3, 0)`, optix `(9, 0, 0)`, vulkan `(0, 1, 0)`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.008876 | 2.130956 | 2.554860 | 0.032996 | 0.002722 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.049609 | 0.008589 | 0.007502 | 0.381387 | 0.007845 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.098995 | 0.021371 | 0.014694 | 1.510656 | 0.020961 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.313028 | 0.032431 | 0.028554 | 6.020820 | 0.038705 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.001969 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.000907 | 0.000379 | 0.000390 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.024286 | 0.023762 | 0.023743 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.001948 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.007606 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.003525 | 0.001503 | 0.001450 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.377668 | 0.375548 | 0.375801 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.007631 | 0.000000 | 0.000000 |

## Interpretation

- all listed PostGIS-backed rows are parity-clean
- the fastest RTDL backend on these rows is now CPU, Embree, or Vulkan rather than OptiX
- CPU and Embree track each other closely on this family after the candidate-index redesign
- the current Vulkan numbers reflect the accepted correctness-first runtime boundary for this family
  rather than a native optimized traversal implementation
