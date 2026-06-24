# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `8384a38376567fe518d89721453eb4433de08312`
- Scale: `large`
- Case repeat: `9`
- Generated: `2026-06-22T14:04:27+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| librts_spatial_index | aabb_index_all_count_only | 0.0413488 | 0.225418 | 0.183x | {"embree": "run_phases.query_median_sec", "optix": "run_phases.query_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| librts_spatial_index | librts_embree_aabb_index | embree | ok | 0.0413488 | run_phases.query_median_sec |
| librts_spatial_index | librts_optix_aabb_index | optix | ok | 0.225418 | run_phases.query_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
