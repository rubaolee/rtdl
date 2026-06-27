# Goal 128 Segment/Polygon Any-Hit Rows Linux Large-Scale Performance

- Generated: `2026-04-06T21:54:01`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `[0, 1, 0]`, embree `[4, 3, 0]`, optix `[9, 0, 0]`, vulkan `[0, 1, 0]`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.003122 | 0.002391 | 0.001997 | 0.001928 | 0.002033 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.014135 | 0.008675 | 0.007810 | 0.007582 | 0.007244 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.029485 | 0.017032 | 0.022807 | 0.014930 | 0.022376 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.052019 | 0.034223 | 0.038180 | 0.037047 | 0.028797 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x2048` | 20480 | 4096 | 0.147442 | 0.078248 | 0.070950 | 0.071373 | 0.071137 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x4096` | 40960 | 8192 | 0.419224 | 0.154114 | 0.143328 | 0.140265 | 0.136616 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.002040 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.000957 | 0.000433 | 0.000405 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.000972 | 0.000395 | 0.000370 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.000943 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.007937 | n/a | n/a |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.003684 | 0.001694 | 0.001651 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.003549 | 0.001569 | 0.001538 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.006193 | n/a | n/a |
