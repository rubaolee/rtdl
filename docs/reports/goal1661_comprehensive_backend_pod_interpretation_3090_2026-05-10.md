# Goal1661 Comprehensive Backend Pod Interpretation - RTX 3090 - 2026-05-10

## Verdict

The RTX 3090 pod run completed with `58` measured OK rows, `0` failed executed rows, and `37` explicitly unsupported rows.

This is measured evidence only. It does not publish `v1.6.11`, authorize a tag, or authorize broad public speedup wording.

## Scope

- Pod GPU: NVIDIA GeForce RTX 3090
- Driver: 580.159.03
- CUDA reported by `nvidia-smi`: 13.0
- CUDA toolkit used by `nvcc`: 12.4
- Current candidate commit: `9b54159fb07cdcdc0d99ac89aff3484a0bbf61b2`
- Baseline commit: `b9c9620af78a2fab92083d43af312bb6310e452a`
- Baseline tag: `v1.0`
- Comparison modes: `embree_1t`, `embree_auto`, `optix`
- Raw result: `docs/reports/goal1661_comprehensive_backend_pod_results_3090_2026-05-10.json`
- Generated summary: `docs/reports/goal1661_comprehensive_backend_pod_summary_3090_2026-05-10.md`
- Full log package: `docs/reports/goal1661_comprehensive_backend_pod_results_3090_2026-05-10.tgz`

## Key Current v1.6.11 Backend Rows

| App | Embree auto sec | OptiX sec | OptiX/Embree speedup |
| --- | ---: | ---: | ---: |
| polygon_set_jaccard | 399.070 | 6.760 | 59.031 |
| robot_collision_screening | 9.068 | 1.857 | 4.883 |
| hausdorff_distance | 7.266 | 2.161 | 3.362 |
| ann_candidate_search | 4.297 | 2.233 | 1.924 |
| barnes_hut_force_app | 9.574 | 4.818 | 1.987 |
| polygon_pair_overlap_area_rows | 10.708 | 5.656 | 1.893 |
| facility_knn_assignment | 3.675 | 2.018 | 1.821 |

## 4090 Cross-Check

The 3090 run agrees with the 4090 run on the main qualitative result: long RT-heavy current `v1.6.11` rows show strong OptiX wins, while short rows are not universal GPU wins.

| App | 3090 OptiX sec | 4090 OptiX sec | 3090/4090 OptiX ratio |
| --- | ---: | ---: | ---: |
| polygon_set_jaccard | 6.760 | 5.178 | 1.306 |
| polygon_pair_overlap_area_rows | 5.656 | 3.786 | 1.494 |
| robot_collision_screening | 1.857 | 1.385 | 1.341 |
| hausdorff_distance | 2.161 | 1.681 | 1.285 |
| barnes_hut_force_app | 4.818 | 3.645 | 1.322 |
| facility_knn_assignment | 2.018 | 1.682 | 1.200 |
| ann_candidate_search | 2.233 | 1.808 | 1.235 |

## Cross-Version Findings

The accepted `v1.0` versus `v1.6.11` rows remain mixed and mostly close. The 3090 run does not support a broad `v1.6.11` over `v1.0` speedup claim.

Examples:

- `polygon_set_jaccard` OptiX: `v1.0` 6.287s, `v1.6.11` 6.760s, speedup 0.930.
- `robot_collision_screening` OptiX: `v1.0` 1.550s, `v1.6.11` 1.857s, speedup 0.835.
- `database_analytics` OptiX: `v1.0` 3.441s, `v1.6.11` 3.664s, speedup 0.939.
- `service_coverage_gaps` OptiX: `v1.0` 1.847s, `v1.6.11` 2.144s, speedup 0.862.

## Unsupported Rows

Unsupported rows are expected and were not counted as wins or losses. They have the same interpretation as the RTX 4090 run:

- Most unsupported rows are `v1.0` app surfaces without a stable Embree backend selector.
- Some rows lack a real engine selector and would be decorative labels rather than real backend comparisons.
- Some app entries are excluded from the v1.6.11 Embree/OptiX pod command set.
- DBSCAN is a shared fixed-radius primitive alias and is not an independent timing row.

## Conclusion

The 3090 run independently confirms the central performance story from the 4090 run: current `v1.6.11` has real app-generic backend surfaces, and OptiX provides large wins on selected long RT-heavy workloads. It also reinforces the boundary that RTDL should not claim universal GPU speedup, universal version speedup, or wins on unsupported rows.
