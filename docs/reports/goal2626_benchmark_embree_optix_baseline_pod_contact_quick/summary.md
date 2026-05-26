# Goal2626 Embree vs OptiX Baseline

This artifact is an internal baseline for evaluating a future Triton/Numba partner path without new C++.
It is not a public speedup claim.

- Commit: `0a2ed76efeab07e79ccad004b978befde0d383db`
- Scale: `quick`
- Case repeat: `3`
- Generated: `2026-05-26T18:48:26+0000`

## Ratios

| App | Group | Embree sec | OptiX sec | OptiX speedup vs Embree | Metric source |
| --- | --- | ---: | ---: | ---: | --- |
| contact_manifold | native_collect_k_i64 | 0.000313761 | 0.000390131 | 0.804x | {"embree": "native_collect_elapsed_sec", "optix": "native_collect_elapsed_sec"} |

## Case Results

| App | Case | Backend | Status | Primary sec | Source or reason |
| --- | --- | --- | --- | ---: | --- |
| contact_manifold | contact_manifold_embree_native_collect_k | embree | ok | 0.000313761 | native_collect_elapsed_sec |
| contact_manifold | contact_manifold_optix_native_collect_k | optix | ok | 0.000390131 | native_collect_elapsed_sec |

## Boundary

- Unsupported Embree rows are recorded as runtime coverage gaps, not failures of the app.
- `process_wall_median_sec` includes Python process startup and is weaker than app-internal timing.
- Rows with different comparison groups are not ratioed.
- Use these numbers as before/after baselines for the next partner path; do not use them as broad public claims without review.
