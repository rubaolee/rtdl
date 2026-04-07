# Goal 128 Segment/Polygon Any-Hit Rows Linux Large-Scale Performance

- Generated: `2026-04-06T20:52:49`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- Versions: oracle `(0, 1, 0)`, embree `(4, 3, 0)`, optix `(9, 0, 0)`, vulkan `(0, 1, 0)`

## PostGIS-Backed Large-Scale Results

| Dataset | Segments | Polygons | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 640 | 128 | 0.003253 | 0.010866 | 0.010686 | 0.006354 | 0.003331 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 2560 | 512 | 0.015174 | 0.008591 | 0.012124 | 0.007125 | 0.007383 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 5120 | 1024 | 0.030755 | 0.016822 | 0.014740 | 0.014660 | 0.014616 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 10240 | 2048 | 0.054076 | 0.033509 | 0.030137 | 0.036671 | 0.029602 | `True` |

## Current And Prepared Timings

| Dataset | Backend | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | ---: | ---: | ---: |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `cpu` | 0.001996 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `embree` | 0.000943 | 0.000433 | 0.000408 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `optix` | 0.002511 | 0.000397 | 0.000369 |
| `derived/br_county_subset_segment_polygon_tiled_x64` | `vulkan` | 0.000933 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `cpu` | 0.007760 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `embree` | 0.003588 | 0.001681 | 0.001627 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `optix` | 0.003443 | 0.001557 | 0.001506 |
| `derived/br_county_subset_segment_polygon_tiled_x256` | `vulkan` | 0.005296 | 0.000000 | 0.000000 |
