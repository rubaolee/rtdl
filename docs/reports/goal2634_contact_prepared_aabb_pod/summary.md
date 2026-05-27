# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `56e1f9b230cdef6d803191c8804f192133b4d020`
- Scale: `standard`
- Case repeat: `3`
- Generated: `2026-05-27T04:34:20+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| contact_manifold | generic_aabb_broadphase_collect_k | 0.499879 | 0.0166002 | 30.1x | {"embree": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec", "optix": "run_phases.emit_aabb_intersection_pair_rows_2d_median_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| contact_manifold | contact_manifold_embree_aabb_broadphase_collect_k | embree | ok | 0.499879 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |
| contact_manifold | contact_manifold_optix_aabb_broadphase_collect_k | optix | ok | 0.0166002 | run_phases.emit_aabb_intersection_pair_rows_2d_median_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
