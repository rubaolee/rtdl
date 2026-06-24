# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `0005a05193920fe1b6a66e91d0108ce41d2f1ce8`
- Scale: `standard`
- Case repeat: `1`
- Generated: `2026-05-27T03:10:50+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| raydb_style | raydb_grouped_count | 0.211074 | 0.000732717 | 288x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |
| raydb_style | raydb_grouped_sum | 0.198884 | 0.000954303 | 208x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| raydb_style | raydb_embree_count | embree | ok | 0.211074 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_count | optix | ok | 0.000732717 | metadata.timings.query_median_sec |
| raydb_style | raydb_embree_sum | embree | ok | 0.198884 | metadata.timings.query_sec |
| raydb_style | raydb_optix_partner_resident_sum | optix | ok | 0.000954303 | metadata.timings.query_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
