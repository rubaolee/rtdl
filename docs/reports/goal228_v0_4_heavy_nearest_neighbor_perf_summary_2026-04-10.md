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
| postgis | True | True | n/a | 45632 | 12 | 837.179 | 834.415 | 889.626 | 10098.298 |
| cpu | True | True | 0.0 | 45632 | 3 | 3643.792 | 3642.781 | 3652.019 | 10938.592 |
| embree | False | False | None | 45626 | 146 | 67.293 | 66.35 | 259.071 | 10044.151 |
| optix | False | False | None | 45626 | 85 | 110.228 | 109.631 | 769.962 | 10049.84 |
| vulkan | False | False | None | 45626 | 99 | 96.629 | 95.077 | 531.347 | 10019.7 |

## knn_rows / natural_earth_tiled

- Query points: `459`
- Search points: `7342`
- PostGIS ground-truth rows: `1377`

| Backend | Parity | Key Match | Max Abs Err | Rows | Iterations | Median ms | Min ms | Max ms | Total ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| postgis | True | True | n/a | 1377 | 4 | 3154.728 | 3146.657 | 3246.391 | 12702.503 |
| cpu | True | True | 0.0 | 1377 | 51 | 194.54 | 194.001 | 222.488 | 10012.594 |
| embree | True | True | 0.0 | 1377 | 16 | 631.233 | 629.705 | 661.663 | 10134.748 |
| optix | True | True | 1.0643e-05 | 1377 | 917 | 10.567 | 10.382 | 352.971 | 10004.054 |
| vulkan | True | True | 1.0643e-05 | 1377 | 932 | 10.618 | 10.348 | 102.506 | 10004.441 |
