# RTDL Embree Evaluation Summary

- Generated: `2026-03-30T23:47:05`
- Iterations: `3`
- Warmup: `1`
- Host: `macOS-26.3-arm64-arm-64bit-Mach-O`

## Evaluation Matrix

| Case | Workload | Dataset | Category | Parity | CPU Mean (s) | Embree Mean (s) | Speedup |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `lsi_authored_minimal` | `lsi` | `authored_lsi_minimal` | `authored` | `True` | 0.000019 | 0.000139 | 0.134x |
| `lsi_county_slice` | `lsi` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `fixture` | `True` | 0.000081 | 0.000180 | 0.449x |
| `lsi_county_tiled_x8` | `lsi` | `derived/br_county_subset_segments_tiled_x8` | `derived` | `True` | 0.000704 | 0.000413 | 1.702x |
| `pip_authored_minimal` | `pip` | `authored_pip_minimal` | `authored` | `True` | 0.000016 | 0.000148 | 0.107x |
| `pip_county_polygons` | `pip` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `fixture` | `True` | 0.000078 | 0.000235 | 0.330x |
| `pip_county_tiled_x8` | `pip` | `derived/br_county_subset_polygons_tiled_x8` | `derived` | `True` | 0.001117 | 0.000450 | 2.481x |
| `overlay_authored_minimal` | `overlay` | `authored_overlay_minimal` | `authored` | `True` | 0.000029 | 0.000123 | 0.239x |
| `overlay_county_soil_fixture` | `overlay` | `tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb` | `fixture` | `True` | 0.000112 | 0.000211 | 0.532x |
| `overlay_county_soil_tiled_x8` | `overlay` | `derived/br_county_soil_polygons_tiled_x8` | `derived` | `True` | 0.000275 | 0.000614 | 0.447x |
| `ray_authored_minimal` | `ray_tri_hitcount` | `authored_ray_tri_minimal` | `authored` | `True` | 0.000041 | 0.000160 | 0.255x |
| `ray_synthetic_small` | `ray_tri_hitcount` | `examples/reference/rtdl_ray_tri_hitcount.py synthetic random generators` | `synthetic` | `True` | 0.001173 | 0.000223 | 5.271x |
| `ray_synthetic_medium` | `ray_tri_hitcount` | `synthetic/ray_tri_medium` | `synthetic` | `True` | 0.015852 | 0.000437 | 36.244x |
| `ray_synthetic_large` | `ray_tri_hitcount` | `synthetic/ray_tri_large` | `synthetic` | `True` | 0.300874 | 0.001822 | 165.138x |
| `segment_polygon_authored_minimal` | `segment_polygon_hitcount` | `authored_segment_polygon_minimal` | `authored` | `True` | 0.000045 | 0.000178 | 0.255x |
| `segment_polygon_county_fixture` | `segment_polygon_hitcount` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `fixture` | `True` | 0.000339 | 0.000294 | 1.152x |
| `point_nearest_authored_minimal` | `point_nearest_segment` | `authored_point_nearest_segment_minimal` | `authored` | `True` | 0.000021 | 0.000194 | 0.110x |
| `point_nearest_county_fixture` | `point_nearest_segment` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `fixture` | `True` | 0.000126 | 0.000249 | 0.506x |

## Key Findings

- All evaluation cases passed CPU-vs-Embree parity checks.
- Fastest Embree case: overlay_authored_minimal at 0.000123s mean.
- Slowest Embree case: ray_synthetic_large at 0.001822s mean.
- Best Embree speedup vs CPU: ray_synthetic_large at 165.14x.
- lsi largest evaluated local case: lsi_county_tiled_x8 (0.000413s Embree mean).
- pip largest evaluated local case: pip_county_tiled_x8 (0.000450s Embree mean).
- overlay largest evaluated local case: overlay_county_soil_tiled_x8 (0.000614s Embree mean).
- ray_tri_hitcount largest evaluated local case: ray_synthetic_large (0.001822s Embree mean).

## Figures

- `figures/latency_by_case.svg`
- `figures/speedup_by_case.svg`
- `figures/scaling_by_workload.svg`
