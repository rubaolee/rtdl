# Goal1401: v1.5 Standalone Same-Contract Correctness Matrix

Date: 2026-05-06

## Decision

v1.5 standalone release still must not be tagged. The same-contract per-app
correctness gate is now explicitly modeled and completed for local app-contract
evidence after Goal1402. The remaining release blockers are collection
resolution, benchmarks, support/maturity, and release wording.

## Matrix Result

- Public apps tracked: 18
- Standalone included apps: 14
- Standalone excluded apps: 4
- Covered by existing local tests: 14
- Pending exact same-contract execution: 0

Covered apps:

- `database_analytics`
- `graph_analytics`
- `service_coverage_gaps`
- `event_hotspot_screening`
- `facility_knn_assignment`
- `road_hazard_screening`
- `segment_polygon_hitcount`
- `polygon_pair_overlap_area_rows`
- `hausdorff_distance`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`
- `robot_collision_screening`
- `barnes_hut_force_app`

Pending apps:

- none

Excluded apps:

- `segment_polygon_anyhit_rows`
- `polygon_set_jaccard`
- `apple_rt_demo`
- `hiprt_ray_triangle_hitcount`

## Release-Gate Impact

`same_contract_per_app_correctness` is true in
`v1_5_standalone_release_gate` after Goal1402 closure tests. This does not
authorize v1.5 release by itself.

Remaining release blockers:

- `collect_k_bounded_resolution`
- `same_contract_per_app_benchmarks`
- `test_backed_support_maturity_matrix`
- `release_docs_and_public_wording`

## Validation Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1401_v1_5_standalone_correctness_matrix_test \
  tests.goal1402_v1_5_pending_app_correctness_closure_test \
  tests.goal1400_v1_5_standalone_app_classification_test \
  tests.goal1398_v1_5_standalone_release_gate_test
```
