# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `f37ed4bc2dbcfe262e70c5d3c5d5de043a3df748`
- Scale: `large`
- Case repeat: `1`
- Generated: `2026-05-26T23:10:48+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| triangle_counting | triangle_count_summary | 0.911611 | 1.82636 | 0.499x | {"embree": "process_wall_median_sec", "optix": "process_wall_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| triangle_counting | triangle_counting_embree_summary | embree | ok | 0.911611 | process_wall_median_sec |
| triangle_counting | triangle_counting_optix_summary | optix | ok | 1.82636 | process_wall_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
