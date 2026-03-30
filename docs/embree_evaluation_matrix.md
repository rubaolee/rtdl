# Embree Evaluation Matrix

This document freezes the Goal 9 evaluation matrix for the RTDL Embree baseline.

The current matrix is:

| Case ID | Workload | Dataset | Category | Provenance |
| --- | --- | --- | --- | --- |
| `lsi_authored_minimal` | `lsi` | `authored_lsi_minimal` | `authored` | Hand-authored segment sanity case. |
| `lsi_county_slice` | `lsi` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `fixture` | Deterministic county-derived segment slice from the checked-in RayJoin-aligned subset. |
| `lsi_county_tiled_x8` | `lsi` | `derived/br_county_subset_segments_tiled_x8` | `derived` | County subset segment view tiled eight times with fixed offsets. |
| `pip_authored_minimal` | `pip` | `authored_pip_minimal` | `authored` | Hand-authored point-in-polygon sanity case. |
| `pip_county_polygons` | `pip` | `tests/fixtures/rayjoin/br_county_subset.cdb` | `fixture` | County subset fixture converted to probe points and deterministic chain-derived polygons. |
| `pip_county_tiled_x8` | `pip` | `derived/br_county_subset_polygons_tiled_x8` | `derived` | County subset point/polygon views tiled eight times with fixed offsets. |
| `overlay_authored_minimal` | `overlay` | `authored_overlay_minimal` | `authored` | Hand-authored overlay seed sanity case. |
| `overlay_county_soil_fixture` | `overlay` | `tests/fixtures/rayjoin/br_county_subset.cdb + tests/fixtures/rayjoin/br_soil_subset.cdb` | `fixture` | County and soil subset fixtures converted to deterministic chain-derived polygons. |
| `overlay_county_soil_tiled_x8` | `overlay` | `derived/br_county_soil_polygons_tiled_x8` | `derived` | County and soil polygon views tiled eight times with fixed offsets. |
| `ray_authored_minimal` | `ray_tri_hitcount` | `authored_ray_tri_minimal` | `authored` | Hand-authored finite-ray hit-count sanity case. |
| `ray_synthetic_small` | `ray_tri_hitcount` | `examples/rtdl_ray_tri_hitcount.py synthetic random generators` | `synthetic` | Canonical random helper generators with fixed seeds. |
| `ray_synthetic_medium` | `ray_tri_hitcount` | `synthetic/ray_tri_medium` | `synthetic` | Medium deterministic synthetic ray/triangle case. |
| `ray_synthetic_large` | `ray_tri_hitcount` | `synthetic/ray_tri_large` | `synthetic` | Large deterministic synthetic ray/triangle case. |

Rules for this matrix:

- Every case must pass CPU-vs-Embree parity before timing results are reported.
- The output precision mode remains `float_approx`.
- Derived datasets must be reproducible from checked-in fixtures or deterministic helper generators.
- Any future added case should be recorded in both this document and `src/rtdsl/evaluation_matrix.py`.
