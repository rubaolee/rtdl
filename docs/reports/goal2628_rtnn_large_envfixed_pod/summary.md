# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `f37ed4bc2dbcfe262e70c5d3c5d5de043a3df748`
- Scale: `large`
- Case repeat: `1`
- Generated: `2026-05-26T23:05:23+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| rtnn | prepared_3d_ranked_summary | 3.05733 | 0.00974733 | 314x | {"embree": "elapsed_sec", "optix": "elapsed_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| rtnn | rtnn_embree_prepared_3d_ranked_summary | embree | ok | 3.05733 | elapsed_sec |
| rtnn | rtnn_optix_prepared_3d_ranked_summary | optix | ok | 0.00974733 | elapsed_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
