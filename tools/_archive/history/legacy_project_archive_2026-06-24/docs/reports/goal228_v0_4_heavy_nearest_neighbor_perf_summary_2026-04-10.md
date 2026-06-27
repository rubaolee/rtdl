# Goal 228 Heavy Linux v0.4 Nearest-Neighbor Benchmark

- Dataset URL: `https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_populated_places_simple.geojson`
- Base points: `7342`
- Min timed window per backend: `10.0` seconds
- Fixed-radius workload size: `copies=16`, `query_stride=4`
- kNN workload size: `copies=1`, `query_stride=16`

## fixed_radius_neighbors / natural_earth_tiled

- Query points: `29368`
- Search points: `117472`
- PostGIS ground-truth rows: `45632`

| Backend | Parity | Key Match | Max Abs Err | Rows | Iterations | Median ms | Min ms | Max ms | Total ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| postgis | True | True | n/a | 45632 | 12 | 834.03 | 832.612 | 893.35 | 10065.678 |
| cpu | True | True | 0.0 | 45632 | 3 | 3633.902 | 3632.135 | 3643.539 | 10909.575 |
| embree | True | True | 0.0 | 45632 | 147 | 66.937 | 66.016 | 252.219 | 10047.15 |
| optix | True | True | 0.0 | 45632 | 75 | 125.383 | 124.297 | 787.126 | 10072.768 |
| vulkan | True | True | 0.0 | 45632 | 81 | 118.369 | 114.783 | 546.964 | 10030.793 |

## knn_rows / natural_earth_tiled

- Query points: `459`
- Search points: `7342`
- PostGIS ground-truth rows: `1377`

| Backend | Parity | Key Match | Max Abs Err | Rows | Iterations | Median ms | Min ms | Max ms | Total ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| postgis | True | True | n/a | 1377 | 4 | 3158.1 | 3154.911 | 3209.506 | 12680.617 |
| cpu | True | True | 0.0 | 1377 | 51 | 197.423 | 196.828 | 226.318 | 10166.807 |
| embree | True | True | 0.0 | 1377 | 16 | 628.572 | 626.864 | 634.882 | 10066.823 |
| optix | True | True | 1.0643e-05 | 1377 | 918 | 10.565 | 10.387 | 345.874 | 10009.483 |
| vulkan | True | True | 1.0643e-05 | 1377 | 931 | 10.599 | 10.341 | 102.323 | 10006.058 |
