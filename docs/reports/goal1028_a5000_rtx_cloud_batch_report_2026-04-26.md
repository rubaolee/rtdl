# Goal1028 A5000 RTX Cloud Batch Report

Date: 2026-04-26

Source commit: `b70fe3f263fa2be1a7eb6a61fdbba075537644b1`

Cloud host: Runpod container `3999708af092`

GPU: NVIDIA RTX A5000, 24564 MiB VRAM

Driver / CUDA runtime reported by `nvidia-smi`: `580.126.09` / `13.0`

CUDA toolkit used for build: `/usr/local/cuda-12.4`, `nvcc 12.4.131`

OptiX headers: `/workspace/vendor/optix-dev-9.0.0`, tag `v9.0.0`

## Verdict

Status: `evidence_collected_no_public_speedup_claim`.

The planned A-H RTX cloud batch completed on real RTX-class hardware. All final group summaries have `status: ok`, `failed_count: 0`, and analyzer `failure_count: 0`.

This report does not authorize public RTX speedup claims. The artifacts are evidence for bounded RTX/OptiX subpaths and must still be reviewed against same-semantics baselines before public speedup wording is allowed.

## Dependency Repair

The first graph group run failed because the pod lacked `libgeos_c`; native graph BFS and triangle-count checks needed the CPU oracle build. Installing `libgeos-dev` and `pkg-config` fixed the environment, and the rerun passed.

This was a pod dependency failure, not an OptiX graph visibility traversal failure. The final saved `goal761_group_f_graph_summary.json` is the passing rerun.

## Traceability Caveat

The cloud copy was staged with `git archive`, so the pod directory was not a git checkout. The group summaries therefore contain `git_head: fatal: not a git repository`. The source commit is still recorded through `.rtdl_source_commit` and the runner `source_commit` field:

`b70fe3f263fa2be1a7eb6a61fdbba075537644b1`

Future cloud runners should inject this source commit into the analyzer reports directly instead of relying on `git rev-parse`.

## Group Results

| Group | Scope | Entries | Final Status | Analyzer |
|---|---|---:|---|---|
| A | Robot collision prepared pose flags | 1 | `ok` | `ok` |
| B | Outlier / DBSCAN fixed-radius prepared paths | 2 | `ok` | `ok` |
| C | Database analytics prepared compact summaries | 2 | `ok` | `ok` |
| D | Service coverage, hotspot, facility coverage prepared paths | 3 | `ok` | `ok` |
| E | Road hazard and segment/polygon native gates | 3 | `ok` | `ok` |
| F | Graph visibility plus native graph-ray BFS / triangle gate | 1 | `ok` after GEOS install | `ok` |
| G | Hausdorff, ANN, Barnes-Hut prepared decision paths | 3 | `ok` | `ok` |
| H | Polygon pair overlap and polygon set Jaccard native-assisted gates | 2 | `ok` | `ok` |

## App Evidence Table

| App | RTX subpath exercised | Median native/query time (s) | Prepare/build time (s) | Current claim boundary |
|---|---|---:|---:|---|
| `robot_collision_screening` | prepared pose flags | 0.000357 | scene 1.104788 + rays 0.017696 | Real bounded RT-core path; public speedup wording still needs review against timing floor and baselines. |
| `outlier_detection` | fixed-radius density summary | 0.000854 | 1.288309 | Bounded scalar traversal evidence only, not whole outlier app speedup. |
| `dbscan_clustering` | fixed-radius core flags | 0.000854 | 0.004439 | Bounded core-flag traversal evidence only, not full DBSCAN clustering speedup. |
| `database_analytics:sales_risk` | prepared DB compact summary | 0.084712 | 0.822136 | Prepared DB subpath only; not DBMS or SQL-engine claim. |
| `database_analytics:regional_dashboard` | prepared DB compact summary | 0.118548 | 1.089032 | Prepared DB subpath only; not DBMS or SQL-engine claim. |
| `service_coverage_gaps` | prepared gap summary | 0.147815 | 1.244384 | Prepared compact summary only, not nearest-row or whole-app speedup. |
| `event_hotspot_screening` | prepared count summary | 0.226937 | 1.318315 | Prepared compact summary only, not full hotspot app speedup. |
| `facility_knn_assignment` | coverage threshold prepared | 0.000599 | 1.279376 | Threshold coverage decision only, not ranked KNN assignment. |
| `road_hazard_screening` | native segment/polygon summary gate | 0.134901 | 1.946494 | Experimental prepared road-hazard summary gate only. |
| `segment_polygon_hitcount` | native segment/polygon hit-count | 0.002926 | 1.283442 | Experimental hit-count gate only, not row-returning whole app. |
| `segment_polygon_anyhit_rows` | bounded native pair-row any-hit | 0.004760 | 1.281313 | Experimental bounded row gate only; output capacity matters. |
| `graph_analytics` | visibility any-hit + native graph-ray gate | 1.870180 | not separately reported by analyzer | Bounded graph RT subpaths only; not graph database or whole graph-system acceleration. |
| `hausdorff_distance` | directed threshold prepared | 0.004484 | 1.197953 | Threshold decision only, not exact Hausdorff distance. |
| `ann_candidate_search` | candidate threshold prepared | 0.000726 | 1.098374 | Candidate coverage only, not full ANN index/ranking. |
| `barnes_hut_force_app` | node coverage prepared | 0.001904 | 1.225596 | Node-coverage decision only, not force-vector solver. |
| `polygon_pair_overlap_area_rows` | native-assisted LSI/PIP candidate discovery | 4.250674 | not separately reported by analyzer | Candidate discovery plus native exact continuation only, not monolithic GPU area kernel. |
| `polygon_set_jaccard` | native-assisted LSI/PIP candidate discovery | 3.512444 | not separately reported by analyzer | Candidate discovery plus native exact continuation only, not monolithic GPU Jaccard kernel. |

Group H has large exact-continuation/postprocess cost and must not be evaluated by RT candidate-discovery timing alone:

- `polygon_pair_overlap_area_rows`: candidate discovery `4.250674s`, exact refinement/postprocess `3.324128s`.
- `polygon_set_jaccard`: candidate discovery `3.512444s`, exact refinement/postprocess `5.403336s`.

Groups C, D, F, and H still need explicit same-semantics correctness/baseline review before any public correctness or speedup claim. This cloud batch is artifact collection, not the final claim gate.

## Saved Artifacts

Primary group summaries:

- `docs/reports/goal761_group_a_robot_summary.json`
- `docs/reports/goal761_group_b_fixed_radius_summary.json`
- `docs/reports/goal761_group_c_database_summary.json`
- `docs/reports/goal761_group_d_spatial_summary.json`
- `docs/reports/goal761_group_e_segment_polygon_summary.json`
- `docs/reports/goal761_group_f_graph_summary.json`
- `docs/reports/goal761_group_g_prepared_decision_summary.json`
- `docs/reports/goal761_group_h_polygon_summary.json`

Analyzer reports:

- `docs/reports/goal762_group_a_robot_artifact_report.md`
- `docs/reports/goal762_group_b_fixed_radius_artifact_report.md`
- `docs/reports/goal762_group_c_database_artifact_report.md`
- `docs/reports/goal762_group_d_spatial_artifact_report.md`
- `docs/reports/goal762_group_e_segment_polygon_artifact_report.md`
- `docs/reports/goal762_group_f_graph_artifact_report.md`
- `docs/reports/goal762_group_g_prepared_decision_artifact_report.md`
- `docs/reports/goal762_group_h_polygon_artifact_report.md`

Pulled cloud copies:

- `docs/reports/cloud_pull_2026_04_26/`

## Next Actions

1. Run 2+ AI review on this Goal1028 evidence package.
2. Compare selected app subpaths against same-semantics CPU/Embree/PostGIS or other baselines before any public speedup claim.
3. Keep optimizing the slow high-value paths: graph visibility, polygon overlap/Jaccard, service coverage, event hotspot, and prepared DB compact summaries.
4. Preserve the pod setup note: GEOS dev libraries are required for graph gate CPU oracle checks.
