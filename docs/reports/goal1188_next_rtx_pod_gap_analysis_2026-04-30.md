# Goal1188 Next RTX Pod Gap Analysis

Date: 2026-04-30

This is a planning/gap analysis only. It does not authorize public RTX speedup wording, release, tagging, or another pod run by itself.

## Summary

- valid: `True`
- public apps: `18`
- RT-core ready apps: `16`
- reviewed public wording apps: `10`
- apps needing public-wording evidence: `6`
- non-NVIDIA targets: `2`
- blocked public wording apps: `0`

## Next Pod Recommendation

Do not spend another pod session until the six needs_public_wording_evidence apps have explicit same-contract baseline commands and timing-floor scale choices. The next pod should batch those six rows plus optional ANN/robot timing-only replacements only if their wording contract changes.

## Apps Needing Evidence

| App | Gap | Local prep before pod | Next pod row |
| --- | --- | --- | --- |
| `database_analytics` | public wording not reviewed; latest DB compact-summary timing is just below the 0.1s review floor | prepare a larger same-contract DB compact-summary scale or repeat-count plan that clears the timing floor without changing semantics | rerun compact_summary prepared warm-query with same-contract CPU/Embree baseline and enough work to exceed the public-review timing floor |
| `graph_analytics` | public wording not reviewed for graph visibility/native graph-ray candidate paths | define same-semantics graph visibility-edge and native graph-ray summary baselines; keep BFS orchestration outside the claim | collect graph visibility/native graph-ray timing with matching CPU/Embree baseline and phase metadata |
| `road_hazard_screening` | public wording not reviewed for prepared native road-hazard compact summary | confirm same-contract CPU or Embree baseline for summary output only, not full GIS/routing | collect prepared native summary timing plus same-contract baseline at a scale above the timing floor |
| `polygon_pair_overlap_area_rows` | public wording not reviewed; candidate discovery is RT-assisted but exact area continuation remains separate | split candidate-discovery timing from exact area continuation and define a candidate-only public wording candidate | collect candidate-discovery-only OptiX timing with CPU/Embree candidate baseline; do not claim exact area speedup |
| `polygon_set_jaccard` | public wording not reviewed; chunked candidate discovery is bounded and exact Jaccard continuation remains separate | choose a stable chunk-size contract and same-contract candidate baseline; keep exact Jaccard outside the claim | collect safe-chunk candidate-discovery timing with baseline and explicit chunk metadata |
| `hausdorff_distance` | public wording not reviewed; latest prepared threshold timing is far below the 0.1s review floor | prepare larger/repeated directed_threshold_prepared decision workload while preserving oracle-match semantics | collect prepared threshold decision timing with oracle/baseline and enough repeated work to exceed the timing floor |

## Timing-Only Followups

| App | Status | Next action |
| --- | --- | --- |
| `ann_candidate_search` | public wording reviewed for prepared candidate-coverage decision; Goal1184 ANN row is timing-only | do not promote Goal1184 ANN timing-only row; only rerun if a future claim needs same-contract oracle/baseline at larger scale |
| `robot_collision_screening` | public wording reviewed only for normalized per-pose prepared pose flags; Goal1184 robot row is timing-only | do not promote Goal1184 robot timing-only row into same-total-work speedup; rerun only with normalized baseline contract if wording changes are requested |

## Full Matrix

| App | RT-core | Public wording | Readiness | Perf class | Bucket |
| --- | --- | --- | --- | --- | --- |
| `database_analytics` | `rt_core_ready` | `public_wording_not_reviewed` | `ready_for_rtx_claim_review` | `python_interface_dominated` | `needs_public_wording_evidence` |
| `graph_analytics` | `rt_core_ready` | `public_wording_not_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal` | `needs_public_wording_evidence` |
| `apple_rt_demo` | `not_nvidia_rt_core_target` | `not_nvidia_public_wording_target` | `exclude_from_rtx_app_benchmark` | `not_optix_applicable` | `non_nvidia_target` |
| `service_coverage_gaps` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `reviewed_wording` |
| `event_hotspot_screening` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `reviewed_wording` |
| `facility_knn_assignment` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `reviewed_wording` |
| `road_hazard_screening` | `rt_core_ready` | `public_wording_not_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `needs_public_wording_evidence` |
| `segment_polygon_hitcount` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `reviewed_wording` |
| `segment_polygon_anyhit_rows` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal` | `reviewed_wording` |
| `polygon_pair_overlap_area_rows` | `rt_core_ready` | `public_wording_not_reviewed` | `ready_for_rtx_claim_review` | `python_interface_dominated` | `needs_public_wording_evidence` |
| `polygon_set_jaccard` | `rt_core_ready` | `public_wording_not_reviewed` | `ready_for_rtx_claim_review` | `python_interface_dominated` | `needs_public_wording_evidence` |
| `hausdorff_distance` | `rt_core_ready` | `public_wording_not_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `needs_public_wording_evidence` |
| `ann_candidate_search` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `reviewed_wording` |
| `outlier_detection` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `reviewed_wording` |
| `dbscan_clustering` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `reviewed_wording` |
| `robot_collision_screening` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal` | `reviewed_wording` |
| `barnes_hut_force_app` | `rt_core_ready` | `public_wording_reviewed` | `ready_for_rtx_claim_review` | `optix_traversal_prepared_summary` | `reviewed_wording` |
| `hiprt_ray_triangle_hitcount` | `not_nvidia_rt_core_target` | `not_nvidia_public_wording_target` | `exclude_from_rtx_app_benchmark` | `not_optix_exposed` | `non_nvidia_target` |

## Boundary

This is a planning/gap analysis only. It does not authorize public RTX speedup wording, release, tagging, or another pod run by itself.

