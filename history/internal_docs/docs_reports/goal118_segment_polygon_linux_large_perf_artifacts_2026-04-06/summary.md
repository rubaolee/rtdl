# Goal 118 Segment/Polygon Linux Large-Scale Performance

- Generated: `2026-04-06T08:35:25`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `(0, 1, 0)`, embree `(4, 3, 0)`, optix `(9, 0, 0)`, vulkan `(0, 1, 0)`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.008486 | 0.047770 | 0.047068 | 0.029512 | 0.037252 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.050030 | 0.573057 | 0.578506 | 0.382547 | 0.571698 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.098951 | 2.277086 | 2.308199 | 1.510382 | 2.275099 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.310521 | 9.034734 | 9.173001 | 6.001617 | 9.049110 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.037086 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.036607 | 0.036083 | 0.036070 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.024139 | 0.023923 | 0.023827 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.037033 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.570057 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.575253 | 0.573124 | 0.572878 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.376711 | 0.375377 | 0.374774 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.570595 | 0.000000 | 0.000000 |

## Interpretation

- all listed PostGIS-backed rows are parity-clean
- OptiX is the fastest current RTDL backend on the audited large rows
- Embree tracks the native CPU oracle closely on this family
- the current Vulkan numbers reflect the accepted correctness-first runtime boundary for this family
  rather than a native optimized traversal implementation
