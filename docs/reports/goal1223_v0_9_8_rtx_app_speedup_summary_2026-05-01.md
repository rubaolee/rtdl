# Goal1223 v0.9.8 RTX App Speedup Summary

Date: 2026-05-01

This report summarizes how NVIDIA OptiX/RTX-backed RT traversal is used by each
public app in the v0.9.8 release state. It is intentionally bounded: a speedup
row means only the named RTX/OptiX sub-path has reviewed evidence versus the
reviewed Embree sub-path. It is not a whole-app speedup claim.

## Summary

- Current release: `v0.9.8`
- Reviewed public RTX sub-path speedup rows: `11`
- Broad whole-app RTX speedup claims authorized: `0`
- Non-NVIDIA app rows: `2`
- Primary source: `docs/v1_0_rtx_app_status.md`
- Release boundary source: `docs/release_reports/v0_9_8/support_matrix.md`

## App Table

| App | How RT is used | Effect / boundary | OptiX vs Embree speedup |
| --- | --- | --- | ---: |
| `service_coverage_gaps` | Prepared fixed-radius gap-summary traversal | Counts coverage gaps without row materialization | `1.61x` |
| `event_hotspot_screening` | Prepared fixed-radius count-summary traversal | Counts hotspot candidates only | `1.55x` |
| `outlier_detection` | Prepared fixed-radius scalar threshold-count traversal | Density threshold count only | `4.64x` |
| `dbscan_clustering` | Prepared fixed-radius scalar core-count traversal | Core-count sub-path only, not full clustering | `6.62x` |
| `robot_collision_screening` | Prepared ray/triangle any-hit pose flags | RT traversal for pose collision flags; normalized per-pose only | `918.91x normalized` |
| `facility_knn_assignment` | Prepared fixed-radius coverage-threshold decision | Coverage decision only, not ranked KNN assignment | `80.60x` |
| `road_hazard_screening` | Prepared native segment/polygon compact-summary traversal | Road-hazard traversal/count at 40k copies only | `3.53x` |
| `segment_polygon_hitcount` | Prepared native segment/polygon hit-count traversal | Compact hit-count traversal only | `1.71x` |
| `segment_polygon_anyhit_rows` | Prepared bounded native pair-row traversal | Bounded pair-row traversal only | `3.03x` |
| `ann_candidate_app` | Prepared fixed-radius candidate-coverage decision | Candidate coverage only, not ANN ranking/indexing | `4.86x` |
| `barnes_hut_force_app` | Prepared fixed-radius node-coverage decision | Node-coverage query only, not force reduction | `240.56x` |
| `database_analytics` | Prepared DB compact-summary traversal/filter/grouping | Real OptiX path, but public wording blocked because measured advantage is below the public threshold | `1.12x-1.16x`, blocked |
| `graph_analytics` | Visibility any-hit plus native graph-ray candidate generation | RT-ready sub-paths exist, but no reviewed public speedup wording for the whole graph app | not public-reviewed |
| `polygon_pair_overlap_area_rows` | Native-assisted LSI/PIP candidate discovery | Candidate discovery only; exact area continuation remains outside the claim | not public-reviewed |
| `polygon_set_jaccard` | Native-assisted LSI/PIP candidate discovery | Correctness-ready at safe chunk size, but public speedup wording is blocked | blocked / `n/a` |
| `hausdorff_distance_app` | Prepared fixed-radius Hausdorff threshold decision | Threshold decision only, not exact Hausdorff distance | not public-reviewed |
| `apple_rt_demo_app` | Apple Metal/MPS RT path | Apple-specific app; not a NVIDIA RTX target | n/a |
| `hiprt_ray_triangle_hitcount` | HIPRT-specific ray/triangle hit-count | HIPRT-specific app; not a NVIDIA RTX target | n/a |

## Interpretation

v0.9.8 has reviewed public speedup wording for `11` bounded RTX sub-paths. These
rows demonstrate RTDL can route app-critical kernels through NVIDIA OptiX/RTX
traversal and compact native summary paths, but they do not authorize claims
that RTDL accelerates entire apps.

Several additional apps are RT-ready in code or evidence but remain blocked or
not public-reviewed for speedup wording. The common blockers are same-scale
evidence gaps, speedup below the public threshold, Python/interface dominance,
row materialization, or postprocess/refinement work that is intentionally outside
the RTX claim.

## Claim Boundary

Allowed wording must stay in this form:

> RTDL includes a bounded NVIDIA OptiX/RTX-backed sub-path for `<app>`:
> `<named traversal or compact-summary phase>`. The claim covers that named
> phase only.

Forbidden wording:

- RTDL accelerates the whole app.
- All graph, database, polygon, or spatial analytics are RT-core accelerated.
- `--backend optix` alone means RT cores were used.
- Polygon area/Jaccard refinement, DBMS execution, ANN ranking, graph-system
  analytics, robot planning, or force reduction are fully RTX accelerated.
