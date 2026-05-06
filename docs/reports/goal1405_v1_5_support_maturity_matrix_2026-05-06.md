# Goal1405: v1.5 Support/Maturity Matrix

Date: 2026-05-06

## Decision

The v1.5 support/maturity matrix is complete and test-backed for the standalone
release surface.

The matrix is narrower than the general public app support matrix:

- 14 apps are included in standalone v1.5 with Embree+OptiX support and local
  correctness coverage.
- 4 apps are explicitly excluded from standalone v1.5.

## Included Apps

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

## Excluded Apps

- `segment_polygon_anyhit_rows`
- `polygon_set_jaccard`
- `apple_rt_demo`
- `hiprt_ray_triangle_hitcount`

## Release-Gate Impact

Passed gates now include:

- `primitive_packet_prerequisite`
- `roadmap_consensus`
- `collect_k_bounded_resolution`
- `app_migration_classification`
- `same_contract_per_app_correctness`
- `test_backed_support_maturity_matrix`

Failed gates remain:

- `same_contract_per_app_benchmarks`
- `release_docs_and_public_wording`

## Validation Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1405_v1_5_support_maturity_matrix_test \
  tests.goal1398_v1_5_standalone_release_gate_test \
  tests.goal1400_v1_5_standalone_app_classification_test \
  tests.goal1401_v1_5_standalone_correctness_matrix_test \
  tests.goal1399_collect_k_bounded_resolution_test
```
