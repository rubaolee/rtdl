# Goal1661 Comprehensive Backend Pod Interpretation - 2026-05-10

## Verdict

The RTX 4090 pod run completed with `58` measured OK rows, `0` failed executed rows, and `37` explicitly unsupported rows.

This is measured evidence only. It does not publish `v1.6.11`, authorize a tag, or authorize broad public speedup wording.

## Scope

- Pod GPU: NVIDIA GeForce RTX 4090
- Driver: 550.127.05
- CUDA reported by `nvidia-smi`: 12.4
- Current candidate commit: `e9f3cbb73180b40e87e212bdfe09ebfee0ce085f`
- Baseline commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- Baseline tag: `v1.0`
- Comparison modes: `embree_1t`, `embree_auto`, `optix`
- Raw result: `docs/reports/goal1661_comprehensive_backend_pod_results_2026-05-10.json`
- Generated summary: `docs/reports/goal1661_comprehensive_backend_pod_summary_2026-05-10.md`
- Full log package: `docs/reports/goal1661_comprehensive_backend_pod_results_2026-05-10.tgz`

## Cross-Version Findings

The accepted cross-version rows mostly compare OptiX against OptiX, because most `v1.0` app profilers did not expose a stable Embree backend selector. These rows show small mixed changes rather than a broad version-level speedup.

| App | Mode | v1.0 sec | v1.6.11 sec | v1.6.11/v1.0 speedup |
| --- | --- | ---: | ---: | ---: |
| ann_candidate_search | optix | 1.568 | 1.808 | 0.867 |
| barnes_hut_force_app | optix | 3.506 | 3.645 | 0.962 |
| database_analytics | embree_1t | 2.174 | 2.044 | 1.064 |
| database_analytics | embree_auto | 2.037 | 2.288 | 0.890 |
| database_analytics | optix | 2.516 | 2.689 | 0.935 |
| event_hotspot_screening | optix | 1.779 | 1.670 | 1.065 |
| facility_knn_assignment | optix | 1.790 | 1.682 | 1.064 |
| graph_analytics | optix | 6.409 | 6.316 | 1.015 |
| hausdorff_distance | optix | 1.590 | 1.681 | 0.946 |
| outlier_detection | optix | 2.868 | 2.722 | 1.054 |
| polygon_pair_overlap_area_rows | optix | 3.887 | 3.786 | 1.027 |
| polygon_set_jaccard | optix | 5.433 | 5.178 | 1.049 |
| road_hazard_screening | optix | 3.170 | 3.206 | 0.989 |
| robot_collision_screening | optix | 1.240 | 1.385 | 0.895 |
| segment_polygon_anyhit_rows | optix | 1.272 | 1.484 | 0.857 |
| segment_polygon_hitcount | optix | 1.289 | 1.425 | 0.905 |
| service_coverage_gaps | optix | 1.383 | 1.586 | 0.872 |

## Backend Findings

Within the current `v1.6.11` candidate, OptiX is strongly faster on the long, RT-heavy rows, but not universally faster on short rows where launch/setup overhead dominates.

| App | Embree mode | Embree sec | OptiX sec | OptiX/Embree speedup |
| --- | --- | ---: | ---: | ---: |
| polygon_set_jaccard | embree_auto | 318.889 | 5.178 | 61.590 |
| polygon_pair_overlap_area_rows | embree_auto | 12.996 | 3.786 | 3.432 |
| robot_collision_screening | embree_auto | 8.190 | 1.385 | 5.913 |
| hausdorff_distance | embree_auto | 5.362 | 1.681 | 3.189 |
| barnes_hut_force_app | embree_auto | 7.999 | 3.645 | 2.195 |
| facility_knn_assignment | embree_auto | 3.085 | 1.682 | 1.834 |
| ann_candidate_search | embree_auto | 3.041 | 1.808 | 1.681 |
| database_analytics | embree_auto | 2.288 | 2.689 | 0.851 |
| event_hotspot_screening | embree_auto | 1.034 | 1.670 | 0.619 |
| road_hazard_screening | embree_auto | 2.326 | 3.206 | 0.725 |
| segment_polygon_anyhit_rows | embree_auto | 0.884 | 1.484 | 0.596 |
| segment_polygon_hitcount | embree_auto | 0.851 | 1.425 | 0.597 |
| service_coverage_gaps | embree_auto | 1.064 | 1.586 | 0.671 |

## Unsupported Rows

Unsupported rows are expected and were not counted as wins or losses.

- `24` rows: `v1.0` profiler command has no stable Embree selector for that app.
- `6` rows: source command has no real engine selector and would be a decorative engine label.
- `6` rows: app has no v1.6.11 Embree/OptiX pod command in Goal1659.
- `1` row: DBSCAN is a shared primitive alias of the outlier fixed-radius row and is not an independent timing row.

## Conclusion

The strongest measured story is not that `v1.6.11` is broadly faster than `v1.0`; the accepted cross-version rows are mixed and mostly close. The strongest measured story is that the current Python+RTDL candidate has real app-generic backend surfaces, and on long RT-heavy workloads OptiX can substantially beat Embree on the same app-level command surface.

Public wording should therefore be narrow: cite specific accepted rows, their exact artifacts, and the RTX 4090 environment. Do not claim universal GPU acceleration, universal version speedup, or superiority on short workloads.
