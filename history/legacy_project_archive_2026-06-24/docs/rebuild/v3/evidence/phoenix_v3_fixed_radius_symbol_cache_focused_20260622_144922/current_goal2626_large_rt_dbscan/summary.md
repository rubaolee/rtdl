# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: ``
- Scale: `large`
- Case repeat: `5`
- Generated: `2026-06-22T15:15:48+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| none | no comparable successful Embree/OptiX pairs |  |  |  |  |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| rt_dbscan | rt_dbscan_embree_fixed_radius_rows | embree | ok | 113.315 | elapsed_sec |
| rt_dbscan | rt_dbscan_optix_grouped_stream | optix | failed |  | None |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
