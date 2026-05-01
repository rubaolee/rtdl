# Goal1223 v0.9.8 RTX App Speedup Summary

Date: 2026-05-01

This report summarizes how NVIDIA OptiX/RTX-backed RT traversal is used by each
public app in the v0.9.8 release state. It is intentionally bounded: a speedup
row means only the named RTX/OptiX sub-path has reviewed evidence versus the
reviewed Embree sub-path. It is not a whole-app speedup claim.

## Summary

- Current release: `v0.9.8`
- Reviewed public RTX sub-path speedup rows: `12` on the current post-release branch after Goal1224
- Broad whole-app RTX speedup claims authorized: `0`
- Non-NVIDIA app rows: `2`
- Primary source: `docs/v1_0_rtx_app_status.md`
- Release boundary source: `docs/release_reports/v0_9_8/support_matrix.md`
- Release tag boundary: Goal1224 does not move the `v0.9.8` tag.

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
| `graph_analytics` | Visibility any-hit plus native graph-ray candidate generation | Valid same-contract evidence exists, but OptiX is slower than Embree; no positive public speedup wording is authorized | blocked / `0.50x` |
| `polygon_pair_overlap_area_rows` | Native-assisted LSI/PIP candidate discovery | Valid same-contract evidence exists, but OptiX is slower than Embree; exact area continuation remains outside the claim | blocked / `0.84x` |
| `polygon_set_jaccard` | Native-assisted LSI/PIP candidate discovery | Correctness-ready at safe chunk size, but public speedup wording is blocked | blocked / `n/a` |
| `hausdorff_distance_app` | Prepared fixed-radius Hausdorff threshold decision | Threshold decision only, not exact Hausdorff distance | `13.73x` |
| `apple_rt_demo_app` | Apple Metal/MPS RT path | Apple-specific app; not a NVIDIA RTX target | n/a |
| `hiprt_ray_triangle_hitcount` | HIPRT-specific ray/triangle hit-count | HIPRT-specific app; not a NVIDIA RTX target | n/a |

## Interpretation

The current post-release branch has reviewed public speedup wording for `12`
bounded RTX sub-paths after Goal1224. The `v0.9.8` tag remains unchanged; this
report now records the current branch interpretation of the remaining three
rows. These rows demonstrate RTDL can route app-critical kernels through NVIDIA
OptiX/RTX traversal and compact native summary paths, but they do not authorize
claims that RTDL accelerates entire apps.

Goal1224 resolves the prior not-public-reviewed rows: `hausdorff_distance_app`
is reviewed for the prepared threshold-decision sub-path, while
`graph_analytics` and `polygon_pair_overlap_area_rows` are blocked because valid
same-contract evidence shows OptiX slower than Embree. Several additional apps
are RT-ready in code or evidence but remain blocked for public speedup wording.
The common blockers are same-scale evidence gaps, speedup below the public
threshold, Python/interface dominance, row materialization, or
postprocess/refinement work that is intentionally outside the RTX claim.

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
