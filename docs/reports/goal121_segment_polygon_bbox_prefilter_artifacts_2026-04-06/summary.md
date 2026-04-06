# Goal 118 Segment/Polygon Linux Large-Scale Performance

- Generated: `2026-04-06T12:07:08`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `(0, 1, 0)`, embree `(4, 3, 0)`, optix `(9, 0, 0)`, vulkan `(0, 1, 0)`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.009329 | 0.060078 | 0.048161 | 0.029507 | 0.037214 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.050354 | 0.572587 | 0.576458 | 0.381677 | 0.570471 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.100046 | 2.274452 | 2.285531 | 1.513359 | 2.272879 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.315025 | 9.040836 | 9.114836 | 5.999233 | 9.044485 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.037097 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.036325 | 0.035820 | 0.035808 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.024354 | 0.023821 | 0.023841 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.037412 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.570643 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.570537 | 0.573563 | 0.569111 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.378245 | 0.375484 | 0.375657 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.607216 | 0.000000 | 0.000000 |

## Interpretation

- all listed PostGIS-backed rows are parity-clean
- OptiX is the fastest current RTDL backend on the audited large rows
- Embree tracks the native CPU oracle closely on this family
- the current Vulkan numbers reflect the accepted correctness-first runtime boundary for this family
  rather than a native optimized traversal implementation
