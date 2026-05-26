# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `06b32d9863de416d58a25b93342cffd453b7895d`
- Scale: `standard`
- Case repeat: `1`
- Generated: `2026-05-26T23:39:07+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| raydb_style | raydb_grouped_count | 0.188846 | 0.735789 | 0.257x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_sec"} |
| raydb_style | raydb_grouped_sum | 0.18965 | 0.652427 | 0.291x | {"embree": "metadata.timings.query_sec", "optix": "metadata.timings.query_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| raydb_style | raydb_embree_count | embree | ok | 0.188846 | metadata.timings.query_sec |
| raydb_style | raydb_optix_count | optix | ok | 0.735789 | metadata.timings.query_sec |
| raydb_style | raydb_embree_sum | embree | ok | 0.18965 | metadata.timings.query_sec |
| raydb_style | raydb_optix_sum | optix | ok | 0.652427 | metadata.timings.query_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
