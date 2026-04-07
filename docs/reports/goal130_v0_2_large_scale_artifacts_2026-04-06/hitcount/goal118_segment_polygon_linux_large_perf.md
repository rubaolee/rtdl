# Goal 118 Segment/Polygon Linux Large-Scale Performance

- Generated: `2026-04-06T21:21:20`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `[0, 1, 0]`, embree `[4, 3, 0]`, optix `[9, 0, 0]`, vulkan `[0, 1, 0]`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.008281 | 0.010713 | 0.009943 | 0.006013 | 0.002166 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.050084 | 0.008556 | 0.007390 | 0.007281 | 0.007637 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.098697 | 0.022005 | 0.014765 | 0.014144 | 0.021388 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.312690 | 0.031800 | 0.028724 | 0.029008 | 0.038824 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.001937 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.000912 | 0.000381 | 0.000403 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.000883 | 0.000350 | 0.000331 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.001906 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.007633 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.003495 | 0.001502 | 0.001464 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.003302 | 0.001416 | 0.001371 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.007550 | n/a | n/a |

## Interpretation

- all listed PostGIS-backed rows are parity-clean
- the fastest RTDL backend now depends on the specific redesign state and dataset; consult the table above
- CPU and Embree may track closely when they share the same host-side exact counting strategy
- the current Vulkan numbers reflect the accepted correctness-first runtime boundary for this family
  rather than a native optimized traversal implementation
