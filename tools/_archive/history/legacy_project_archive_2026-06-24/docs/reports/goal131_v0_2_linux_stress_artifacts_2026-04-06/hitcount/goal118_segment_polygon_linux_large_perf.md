# Goal 118 Segment/Polygon Linux Large-Scale Performance

- Generated: `2026-04-06T21:53:56`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `[0, 1, 0]`, embree `[4, 3, 0]`, optix `[9, 0, 0]`, vulkan `[0, 1, 0]`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.008256 | 0.010829 | 0.009896 | 0.006154 | 0.002204 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.050298 | 0.008719 | 0.007642 | 0.007618 | 0.007772 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.102213 | 0.022227 | 0.014798 | 0.014316 | 0.021659 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.311780 | 0.033339 | 0.029067 | 0.029157 | 0.039540 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x2048` | 20480 | 4096 | 0.663881 | 0.076424 | 0.070444 | 0.067085 | 0.075168 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x4096` | 40960 | 8192 | 1.167043 | 0.149339 | 0.133990 | 0.135224 | 0.150495 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.002030 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.000924 | 0.000384 | 0.000363 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.000962 | 0.000367 | 0.000342 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.001946 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.007660 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.003505 | 0.001508 | 0.001460 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.003352 | 0.001386 | 0.001342 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.009916 | n/a | n/a |

## Interpretation

- all listed PostGIS-backed rows are parity-clean
- the fastest RTDL backend now depends on the specific redesign state and dataset; consult the table above
- CPU and Embree may track closely when they share the same host-side exact counting strategy
- the current Vulkan numbers reflect the accepted correctness-first runtime boundary for this family
  rather than a native optimized traversal implementation
