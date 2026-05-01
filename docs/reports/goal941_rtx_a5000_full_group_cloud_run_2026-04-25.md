# Goal941 RTX A5000 Full Group Cloud Run

Date: 2026-04-25

## Verdict

Status: `cloud_artifacts_collected_analyzer_ok`.

The consolidated OOM-safe RTX cloud run completed on a RunPod NVIDIA RTX A5000. Bootstrap passed, Groups A-H passed, every group artifact was copied back, and Goal762 artifact analysis returned `ok` with zero failures for all eight groups.

This report does not authorize public speedup claims. It records raw cloud evidence for later app-by-app intake, same-semantics baseline comparison, and 2+ AI review.

## Environment

| Field | Value |
|---|---|
| Host | `a6589bc3c61f` |
| GPU | NVIDIA RTX A5000 |
| Driver | `580.126.09` |
| CUDA runtime reported by driver | `13.0` |
| CUDA compiler used | `/usr/local/cuda-12.4/bin/nvcc`, CUDA `12.4.131` |
| OptiX headers | `/workspace/vendor/optix-dev-9.0.0` |
| Python | `3.11.10` |
| Source commit | `7f569829fbad00f9bfa58e758b0fc4ee0324b410` |
| Local artifact directory | `docs/reports/cloud_2026_04_25/runpod_a5000_2026_04_25_0826/` |

Bootstrap artifact: `docs/reports/cloud_2026_04_25/runpod_a5000_2026_04_25_0826/goal763_rtx_cloud_bootstrap_check.json`.

## Bootstrap

| Step | Result |
|---|---|
| `make build-optix` | `ok` |
| Native OptiX focused tests | `30 tests OK` |
| Bootstrap status | `ok` |

## Group Results

| Group | Apps / paths | Entries | Failed | Analyzer |
|---|---|---:|---:|---|
| A | `robot_collision_screening:prepared_pose_flags` | 1 | 0 | `ok` |
| B | `outlier_detection:prepared_fixed_radius_density_summary`, `dbscan_clustering:prepared_fixed_radius_core_flags` | 2 | 0 | `ok` |
| C | `database_analytics:prepared_db_session_sales_risk`, `database_analytics:prepared_db_session_regional_dashboard` | 2 | 0 | `ok` |
| D | `service_coverage_gaps:prepared_gap_summary`, `event_hotspot_screening:prepared_count_summary`, `facility_knn_assignment:coverage_threshold_prepared` | 3 | 0 | `ok` |
| E | `road_hazard_screening:road_hazard_native_summary_gate`, `segment_polygon_hitcount:segment_polygon_hitcount_native_experimental`, `segment_polygon_anyhit_rows:segment_polygon_anyhit_rows_prepared_bounded_gate` | 3 | 0 | `ok` |
| F | `graph_analytics:graph_visibility_edges_gate` | 1 | 0 | `ok` |
| G | `hausdorff_distance:directed_threshold_prepared`, `ann_candidate_search:candidate_threshold_prepared`, `barnes_hut_force_app:node_coverage_prepared` | 3 | 0 | `ok` |
| H | `polygon_pair_overlap_area_rows:polygon_pair_overlap_optix_native_assisted_phase_gate`, `polygon_set_jaccard:polygon_set_jaccard_optix_native_assisted_phase_gate` | 2 | 0 | `ok` |

## Runner Timing Summary

These are runner elapsed times for each manifest entry. They include command process overhead and are not public speedup numbers.

| App | Path | Elapsed sec |
|---|---|---:|
| `robot_collision_screening` | `prepared_pose_flags` | 3.958 |
| `outlier_detection` | `prepared_fixed_radius_density_summary` | 3.072 |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` | 3.072 |
| `database_analytics` | `prepared_db_session_sales_risk` | 4.793 |
| `database_analytics` | `prepared_db_session_regional_dashboard` | 5.395 |
| `service_coverage_gaps` | `prepared_gap_summary` | 3.388 |
| `event_hotspot_screening` | `prepared_count_summary` | 4.071 |
| `facility_knn_assignment` | `coverage_threshold_prepared` | 2.773 |
| `road_hazard_screening` | `road_hazard_native_summary_gate` | 5.877 |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` | 2.112 |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` | 2.307 |
| `graph_analytics` | `graph_visibility_edges_gate` | 6.092 |
| `hausdorff_distance` | `directed_threshold_prepared` | 2.959 |
| `ann_candidate_search` | `candidate_threshold_prepared` | 2.671 |
| `barnes_hut_force_app` | `node_coverage_prepared` | 5.308 |
| `polygon_pair_overlap_area_rows` | `polygon_pair_overlap_optix_native_assisted_phase_gate` | 9.268 |
| `polygon_set_jaccard` | `polygon_set_jaccard_optix_native_assisted_phase_gate` | 10.045 |

## Key Phase Observations

| App / path | Key RTX phase evidence | Correctness / validation evidence |
|---|---|---|
| Robot prepared pose flags | Warm query median `0.000362s`; scene prepare `1.547s`; ray prepare `0.0168s`; pose index prepare `0.000894s`. | Validation intentionally skipped in cloud summary mode; scalar result recorded `colliding_pose_count=193750`. |
| Outlier / DBSCAN fixed-radius summaries | Shared prepared fixed-radius run; warm query medians around `0.001s` at `160000` points. | Artifact reports `matches_oracle=true` for prepared outputs, with validation mode recorded as skipped for cloud timing. |
| DB sales risk | Native DB phase totals exported: traversal `0.0634s`, exact filter `0.0168s`, output pack `0.00683s`, bitset copyback `0.0000696s`; warm query median `0.0867s`. | Compact-summary query status `ok`; no row materialization operations. |
| DB regional dashboard | Native DB phase totals exported: traversal `0.0911s`, exact filter `0.0222s`, output pack `0.0129s`, bitset copyback `0.0000880s`; warm query median `0.126s`. | Compact-summary query status `ok`; no row materialization operations. |
| Facility coverage | OptiX query median `0.000598s`; prepare `1.390s`; pack `0.261s`. | Cloud artifact records threshold result; validation intentionally skipped for this timing path. |
| Road hazard prepared summary | OptiX query median `0.221s`; prepare `1.504s`. | `strict_pass=true`, `matches_oracle=true`, expected and actual digests match. |
| Segment/polygon hit-count | OptiX query median `0.00628s`; prepare `1.054s`. | `strict_pass=true`, `matches_oracle=true`, expected and actual digests match. |
| Segment/polygon bounded pair rows | OptiX query median `0.00471s`; prepare `1.255s`; no overflow. | `strict_pass=true`, `matches_oracle=true`, `emitted_count=2816`, `copied_count=2816`, `overflowed=false`. |
| Graph analytics | Visibility any-hit `2.244s`; native graph-ray BFS `1.052s`; native graph-ray triangle-count `1.224s`. | All three records report `parity_vs_analytic_expected=true`, `strict_pass=true`. |
| Hausdorff threshold | OptiX query median `0.00120s`; prepare `1.420s`. | `matches_oracle=true`, threshold decision true. |
| ANN candidate coverage | OptiX query median `0.000714s`; prepare `1.085s`. | `matches_oracle=true`, threshold decision true. |
| Barnes-Hut node coverage | OptiX query median `0.00180s`; prepare `1.145s`. | `matches_oracle=true`, threshold decision true. |
| Polygon pair overlap | OptiX candidate discovery `4.482s`; CPU exact refinement `3.355s`. | Gate status `pass`. |
| Polygon set Jaccard | OptiX candidate discovery `3.793s`; CPU exact refinement `5.238s`. | Gate status `pass`. |

## Analyzer Outputs

All analyzer outputs are under `docs/reports/cloud_2026_04_25/runpod_a5000_2026_04_25_0826/`:

| Analyzer report | Status | Failures |
|---|---|---:|
| `goal762_a_robot_artifact_report.json` | `ok` | 0 |
| `goal762_b_fixed_radius_artifact_report.json` | `ok` | 0 |
| `goal762_c_database_artifact_report.json` | `ok` | 0 |
| `goal762_d_spatial_artifact_report.json` | `ok` | 0 |
| `goal762_e_segment_polygon_artifact_report.json` | `ok` | 0 |
| `goal762_f_graph_artifact_report.json` | `ok` | 0 |
| `goal762_g_prepared_decision_artifact_report.json` | `ok` | 0 |
| `goal762_h_polygon_artifact_report.json` | `ok` | 0 |

## Claim Boundary

- This run proves the current OOM-safe cloud contract can execute all Groups A-H on real RTX-class NVIDIA hardware.
- This run does not by itself prove whole-app speedups.
- DB, polygon, graph, Hausdorff, ANN, and Barnes-Hut claims must stay bounded to the exact prepared/native sub-paths shown in the artifacts.
- Polygon overlap/Jaccard are native-assisted candidate-discovery paths; exact area/Jaccard refinement remains CPU/Python.
- Graph analytics uses RT traversal for visibility and native graph-ray candidate generation; higher-level BFS/frontier and triangle bookkeeping remain app-owned.
- Public claims still require app-by-app intake, same-semantics baseline comparison, and 2+ AI consensus.

## Operational Notes

- Initial transfer without `.git` produced artifacts with fatal git metadata. Those artifacts were not used as final evidence.
- `.git` metadata was copied to the pod, all Groups A-H were rerun, and final artifacts record source commit `7f569829fbad00f9bfa58e758b0fc4ee0324b410`.
- The pod working tree was intentionally dirty because the runtime package excluded large tracked build/demo artifacts. The source commit is still recorded, and the runtime package included current uncommitted Goal933-940 files required for the run.
- Artifacts were copied back after each group.
