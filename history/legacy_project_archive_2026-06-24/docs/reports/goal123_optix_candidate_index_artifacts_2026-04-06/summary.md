# Goal 123 OptiX Candidate-Index Linux Large-Scale Performance Artifact

- Generated: `2026-04-06T18:08:19`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `(0, 1, 0)`, embree `(4, 3, 0)`, optix `(9, 0, 0)`, vulkan `(0, 1, 0)`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.009207 | 0.011099 | 0.011683 | 0.009804 | 0.002306 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.051580 | 0.008737 | 0.007354 | 0.007160 | 0.007778 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.098630 | 0.021715 | 0.014169 | 0.013913 | 0.021005 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.314453 | 0.033021 | 0.028251 | 0.028282 | 0.038754 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.001952 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.000904 | 0.000390 | 0.000396 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.000878 | 0.000353 | 0.000335 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.001928 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.007566 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.003535 | 0.001531 | 0.001472 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.003307 | 0.001435 | 0.001371 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.007560 | 0.000000 | 0.000000 |

## Interpretation

- all listed PostGIS-backed rows are parity-clean
- after the OptiX alignment step, the fastest RTDL backend on these rows depends on the dataset
- OptiX now tracks the CPU/Embree large-row performance story instead of lagging far behind it
- Embree tracks the native CPU oracle closely on this family
- the current Vulkan numbers reflect the accepted correctness-first runtime boundary for this family
  rather than a native optimized traversal implementation
