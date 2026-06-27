# Goal 128 Segment/Polygon Any-Hit Rows Linux Large-Scale Performance

- Generated: `2026-04-06T21:21:21`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `[0, 1, 0]`, embree `[4, 3, 0]`, optix `[9, 0, 0]`, vulkan `[0, 1, 0]`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.003299 | 0.011075 | 0.009967 | 0.006157 | 0.003111 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.014823 | 0.008495 | 0.011838 | 0.007223 | 0.007199 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.030618 | 0.016451 | 0.014536 | 0.014441 | 0.014550 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.054162 | 0.033502 | 0.029918 | 0.036233 | 0.029532 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.002006 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.000932 | 0.000433 | 0.000405 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.002490 | 0.000395 | 0.000368 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.000923 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.007789 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.003573 | 0.001687 | 0.001628 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.003465 | 0.001554 | 0.001495 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.005288 | n/a | n/a |
