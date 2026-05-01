# Goal942 Goal941 App Intake And Matrix Promotion

Date: 2026-04-25

## Scope

Goal942 intakes the Goal941 RTX A5000 full OOM-safe group run into the public app readiness tables. It promotes only bounded NVIDIA OptiX/RTX-backed sub-paths that have phase-clean Goal941 artifacts and analyzer status `ok`.

This is not release authorization and not a public speedup claim. It is a claim-review readiness update.

## Input Evidence

- Goal941 cloud report: `docs/reports/goal941_rtx_a5000_full_group_cloud_run_2026-04-25.md`
- Goal941 cloud artifacts: `docs/reports/cloud_2026_04_25/runpod_a5000_2026_04_25_0826/`
- Goal941 peer review: `docs/reports/goal941_peer_review_2026-04-25.md`
- Goal941 two-AI consensus: `docs/reports/goal941_two_ai_consensus_2026-04-25.md`
- Current claim-review package: `docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.md`

The Goal941 group run passed bootstrap and groups A-H with `status: ok`, `failed_count: 0`, and source commit `7f569829fbad00f9bfa58e758b0fc4ee0324b410`. The bootstrap artifact still preserves an initial no-`.git` preflight attempt, but the final group artifacts carry the correct source commit.

## Promotion Decisions

| App | Goal941 intake decision | Allowed claim-review scope | Explicit non-claim boundary |
| --- | --- | --- | --- |
| `database_analytics` | Promote to `ready_for_rtx_claim_review` / `rt_core_ready`. | Prepared DB compact-summary traversal/filter/grouping sub-path. | No DBMS, SQL engine, full dashboard, row-materializing output, or broad whole-app speedup claim. |
| `road_hazard_screening` | Promote to `ready_for_rtx_claim_review` / `rt_core_ready`. | Prepared native compact road-hazard summary traversal. | No full GIS/routing, default-app, or broad road-hazard speedup claim. |
| `segment_polygon_hitcount` | Promote to `ready_for_rtx_claim_review` / `rt_core_ready`. | Prepared native compact segment/polygon hit-count traversal. | No broad segment/polygon speedup or pair-row output claim. |
| `segment_polygon_anyhit_rows` | Promote to `ready_for_rtx_claim_review` / `rt_core_ready`. | Prepared bounded native pair-row traversal at reviewed output capacity. | No unbounded pair-row-volume or default-app speedup claim. |
| `hausdorff_distance` | Promote to `ready_for_rtx_claim_review` / `rt_core_ready`. | Prepared Hausdorff <= radius threshold decision. | No exact Hausdorff distance, KNN-row, ranking, or whole-app speedup claim. |
| `ann_candidate_search` | Promote to `ready_for_rtx_claim_review` / `rt_core_ready`. | Prepared ANN candidate-coverage decision. | No ANN index, ranking, FAISS/HNSW/IVF/PQ behavior, recall optimization, or whole-app speedup claim. |
| `barnes_hut_force_app` | Promote to `ready_for_rtx_claim_review` / `rt_core_ready`. | Prepared Barnes-Hut node-coverage decision. | No opening-rule, force-vector reduction, N-body simulation, or whole-app speedup claim. |

Existing ready rows are retained: `graph_analytics`, `service_coverage_gaps`, `event_hotspot_screening`, `facility_knn_assignment`, `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`, `outlier_detection`, `dbscan_clustering`, and `robot_collision_screening`.

Apple RT and HIPRT demo apps remain out of the NVIDIA OptiX/RTX target.

## Current Board

- Ready for RTX claim review: 16 apps/sub-paths.
- Out of NVIDIA target: 2 apps.
- Remaining public speedup authorization: none from this goal.

The current ready set is:

1. `database_analytics`
2. `graph_analytics`
3. `service_coverage_gaps`
4. `event_hotspot_screening`
5. `facility_knn_assignment`
6. `road_hazard_screening`
7. `segment_polygon_hitcount`
8. `segment_polygon_anyhit_rows`
9. `polygon_pair_overlap_area_rows`
10. `polygon_set_jaccard`
11. `hausdorff_distance`
12. `ann_candidate_search`
13. `outlier_detection`
14. `dbscan_clustering`
15. `robot_collision_screening`
16. `barnes_hut_force_app`

## Files Updated

- `src/rtdsl/app_support_matrix.py`
- `README.md`
- `docs/app_engine_support_matrix.md`
- `docs/application_catalog.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- `docs/tutorials/graph_workloads.md`
- `docs/tutorials/nearest_neighbor_workloads.md`
- `docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.md`
- `docs/reports/goal939_current_rtx_claim_review_package_2026-04-25.json`
- `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
- `docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json`

## Verification

Focused local gate:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal815_db_rt_core_claim_gate_test \
  tests.goal817_cuda_through_optix_claim_gate_test \
  tests.goal820_segment_polygon_rt_core_gate_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal937_ready_rtx_claim_review_packet_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test
```

Result: 67 tests OK.

Current live-doc stale-wording sweep found no remaining `after Goal937`, `nine bounded`, `nine apps`, `exactly nine`, `Still held for claim review`, or `remain held for claim review` references in `README.md`, live `docs/*.md`, `docs/tutorials`, `tests`, or `src/rtdsl/app_support_matrix.py`, aside from the historical test class name.

## Boundary

Goal942 makes app/sub-paths ready for claim review. It does not say RTDL beats CPU, Embree, PostGIS, SciPy, FAISS, or any other baseline. Public performance comparisons still require same-semantics baseline review and 2+ AI consensus.
