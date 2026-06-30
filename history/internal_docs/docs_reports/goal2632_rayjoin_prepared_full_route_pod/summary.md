# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `4960079ebe4d72689da49a5bf05cfd824b36a887`
- Scale: `quick`
- Case repeat: `1`
- Generated: `2026-05-27T03:54:40+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| spatial_rayjoin | rayjoin_all_backend_query_summary | 0.0199523 | 0.00053526 | 37.3x | {"embree": "workloads.total_elapsed_sec", "optix": "prepared_query_total_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| spatial_rayjoin | spatial_rayjoin_embree_generic | embree | ok | 0.0199523 | workloads.total_elapsed_sec |
| spatial_rayjoin | spatial_rayjoin_optix_prepared_full_route | optix | ok | 0.00053526 | prepared_query_total_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
