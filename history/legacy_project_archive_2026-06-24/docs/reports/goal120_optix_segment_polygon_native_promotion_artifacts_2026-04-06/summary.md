# Goal 118 Segment/Polygon Linux Large-Scale Performance

- Generated: `2026-04-06T09:01:30`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `(0, 1, 0)`, embree `(4, 3, 0)`, optix `(9, 0, 0)`, vulkan `(0, 1, 0)`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.008962 | 0.053468 | 0.048637 | 0.029681 | 0.037256 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.050481 | 0.572838 | 0.578450 | 0.383164 | 0.577138 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.099124 | 2.275266 | 2.299949 | 1.506938 | 2.269641 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.311981 | 9.031902 | 9.173111 | 6.001533 | 9.037438 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.037068 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.036705 | 0.036125 | 0.036082 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.024354 | 0.023839 | 0.023814 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.037057 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.569883 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.574407 | 0.572332 | 0.573196 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.378534 | 0.376049 | 0.376218 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.570360 | 0.000000 | 0.000000 |

## Interpretation

- all listed PostGIS-backed rows are parity-clean
- OptiX is the fastest current RTDL backend on the audited large rows
- Embree tracks the native CPU oracle closely on this family
- the current Vulkan numbers reflect the accepted correctness-first runtime boundary for this family
  rather than a native optimized traversal implementation
