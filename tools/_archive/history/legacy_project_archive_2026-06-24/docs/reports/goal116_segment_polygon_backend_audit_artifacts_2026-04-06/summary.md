# Goal 116 Segment/Polygon Full Backend Audit

- Generated: `2026-04-06T00:24:15`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`

## Oracle Parity

| Dataset | Backend | Available | Parity vs CPU Python Reference | Row Count |
| --- | --- | --- | --- | ---: |
| `authored_segment_polygon_minimal` | `cpu` | `True` | `True` | 2 |
| `authored_segment_polygon_minimal` | `embree` | `True` | `True` | 2 |
| `authored_segment_polygon_minimal` | `optix` | `True` | `True` | 2 |
| `authored_segment_polygon_minimal` | `vulkan` | `True` | `True` | 2 |
| `tests/fixtures/rayjoin/br_county_subset.cdb` | `cpu` | `True` | `True` | 10 |
| `tests/fixtures/rayjoin/br_county_subset.cdb` | `embree` | `True` | `True` | 10 |
| `tests/fixtures/rayjoin/br_county_subset.cdb` | `optix` | `True` | `True` | 10 |
| `tests/fixtures/rayjoin/br_county_subset.cdb` | `vulkan` | `True` | `True` | 10 |
| `derived/br_county_subset_segment_polygon_tiled_x4` | `cpu` | `True` | `True` | 40 |
| `derived/br_county_subset_segment_polygon_tiled_x4` | `embree` | `True` | `True` | 40 |
| `derived/br_county_subset_segment_polygon_tiled_x4` | `optix` | `True` | `True` | 40 |
| `derived/br_county_subset_segment_polygon_tiled_x4` | `vulkan` | `True` | `True` | 40 |
| `derived/br_county_subset_segment_polygon_tiled_x16` | `cpu` | `True` | `True` | 160 |
| `derived/br_county_subset_segment_polygon_tiled_x16` | `embree` | `True` | `True` | 160 |
| `derived/br_county_subset_segment_polygon_tiled_x16` | `optix` | `True` | `True` | 160 |
| `derived/br_county_subset_segment_polygon_tiled_x16` | `vulkan` | `True` | `True` | 160 |

## Performance

| Dataset | Backend | Available | Parity | Current Mean (s) | Prepared Bind+Run Mean (s) | Prepared Reuse Mean (s) |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `authored_segment_polygon_minimal` | `cpu` | `True` | `True` | 0.000050 | 0.000000 | 0.000000 |
| `authored_segment_polygon_minimal` | `embree` | `True` | `True` | 0.000043 | 0.000016 | 0.000010 |
| `authored_segment_polygon_minimal` | `optix` | `True` | `True` | 0.000040 | 0.000015 | 0.000009 |
| `authored_segment_polygon_minimal` | `vulkan` | `True` | `True` | 0.000061 | 0.000000 | 0.000000 |
| `tests/fixtures/rayjoin/br_county_subset.cdb` | `cpu` | `True` | `True` | 0.000081 | 0.000000 | 0.000000 |
| `tests/fixtures/rayjoin/br_county_subset.cdb` | `embree` | `True` | `True` | 0.000051 | 0.000024 | 0.000017 |
| `tests/fixtures/rayjoin/br_county_subset.cdb` | `optix` | `True` | `True` | 0.000057 | 0.000022 | 0.000016 |
| `tests/fixtures/rayjoin/br_county_subset.cdb` | `vulkan` | `True` | `True` | 0.000080 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x4` | `cpu` | `True` | `True` | 0.000293 | 0.000000 | 0.000000 |
| `derived/br_county_subset_segment_polygon_tiled_x4` | `embree` | `True` | `True` | 0.000216 | 0.000174 | 0.000209 |
| `derived/br_county_subset_segment_polygon_tiled_x4` | `optix` | `True` | `True` | 0.000158 | 0.000124 | 0.000126 |
| `derived/br_county_subset_segment_polygon_tiled_x4` | `vulkan` | `True` | `True` | 0.000296 | 0.000000 | 0.000000 |

## PostGIS Validation

- Current scale dataset: `derived/br_county_subset_segment_polygon_tiled_x64`
- Large scale dataset: `derived/br_county_subset_segment_polygon_tiled_x256`
- Current scale PostGIS SHA256: `bdfe3c868dbae0278436b1451dd5760564f57359096986e0bf95951dc57f507b`
- Large scale PostGIS SHA256: `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099`
