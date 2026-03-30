# RTDL Embree Evaluation Summary

- Generated: `2026-03-30T09:01:52`
- Iterations: `3`
- Warmup: `1`
- Host: `macOS-26.3-arm64-arm-64bit-Mach-O`

## Evaluation Matrix

| Case | Workload | Dataset | Category | Parity | CPU Mean (s) | Embree Mean (s) | Speedup |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| `lsi_authored_minimal` | `lsi` | `authored_lsi_minimal` | `authored` | `True` | 0.000015 | 0.000375 | 0.040x |
| `lsi_county_slice` | `lsi` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `fixture` | `True` | 0.000080 | 0.000187 | 0.428x |
| `lsi_county_tiled_x8` | `lsi` | `derived/br_county_subset_segments_tiled_x8` | `derived` | `True` | 0.000716 | 0.000657 | 1.090x |
| `pip_authored_minimal` | `pip` | `authored_pip_minimal` | `authored` | `True` | 0.000012 | 0.000141 | 0.087x |
| `pip_county_polygons` | `pip` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `fixture` | `True` | 0.000172 | 0.000242 | 0.708x |
| `pip_county_tiled_x8` | `pip` | `derived/br_county_subset_polygons_tiled_x8` | `derived` | `True` | 0.000845 | 0.000531 | 1.592x |
| `overlay_authored_minimal` | `overlay` | `authored_overlay_minimal` | `authored` | `True` | 0.000026 | 0.000222 | 0.119x |
| `overlay_county_soil_fixture` | `overlay` | `tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb` | `fixture` | `True` | 0.000313 | 0.000412 | 0.761x |
| `overlay_county_soil_tiled_x8` | `overlay` | `derived/br_county_soil_polygons_tiled_x8` | `derived` | `True` | 0.000310 | 0.000284 | 1.091x |
| `ray_authored_minimal` | `ray_tri_hitcount` | `authored_ray_tri_minimal` | `authored` | `True` | 0.000036 | 0.000118 | 0.308x |
| `ray_synthetic_small` | `ray_tri_hitcount` | `examples/rtdl_ray_tri_hitcount.py synthetic random generators` | `synthetic` | `True` | 0.001112 | 0.000397 | 2.799x |
| `ray_synthetic_medium` | `ray_tri_hitcount` | `synthetic/ray_tri_medium` | `synthetic` | `True` | 0.014991 | 0.000739 | 20.292x |
| `ray_synthetic_large` | `ray_tri_hitcount` | `synthetic/ray_tri_large` | `synthetic` | `True` | 0.221587 | 0.001233 | 179.740x |

## Key Findings

- All evaluation cases passed CPU-vs-Embree parity checks.
- Fastest Embree case: ray_authored_minimal at 0.000118s mean.
- Slowest Embree case: ray_synthetic_large at 0.001233s mean.
- Best Embree speedup vs CPU: ray_synthetic_large at 179.74x.
- lsi largest evaluated local case: lsi_county_tiled_x8 (0.000657s Embree mean).
- pip largest evaluated local case: pip_county_tiled_x8 (0.000531s Embree mean).
- overlay largest evaluated local case: overlay_county_soil_tiled_x8 (0.000284s Embree mean).
- ray_tri_hitcount largest evaluated local case: ray_synthetic_large (0.001233s Embree mean).

## Figures

- `figures/latency_by_case.svg`
- `figures/speedup_by_case.svg`
- `figures/scaling_by_workload.svg`
