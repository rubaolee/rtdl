# Goal1401: v1.5 Standalone Same-Contract Correctness Matrix

Date: 2026-05-06

## Decision

v1.5 standalone release still must not be tagged. The same-contract per-app
correctness gate is now explicitly modeled, but it remains incomplete until all
included apps have Embree and OptiX correctness evidence for the same supported
surface.

## Matrix Result

- Public apps tracked: 18
- Standalone included apps: 14
- Standalone excluded apps: 4
- Covered by existing local tests: 10
- Pending exact same-contract execution: 4

Covered apps:

- `database_analytics`
- `graph_analytics`
- `service_coverage_gaps`
- `event_hotspot_screening`
- `facility_knn_assignment`
- `polygon_pair_overlap_area_rows`
- `ann_candidate_search`
- `outlier_detection`
- `dbscan_clustering`
- `robot_collision_screening`

Pending apps:

- `road_hazard_screening`
- `segment_polygon_hitcount`
- `hausdorff_distance`
- `barnes_hut_force_app`

Excluded apps:

- `segment_polygon_anyhit_rows`
- `polygon_set_jaccard`
- `apple_rt_demo`
- `hiprt_ray_triangle_hitcount`

## Release-Gate Impact

`same_contract_per_app_correctness` remains false in
`v1_5_standalone_release_gate`. This is intentional: nearby historical app
tests are not enough for the v1.5 standalone release unless they establish the
same Embree/OptiX contract for the exact included surface.

The next correctness work should add or execute exact Embree/OptiX parity tests
for:

- segment/polygon compact hazard summary
- segment/polygon compact hit-count summary
- Hausdorff threshold decision summary
- Barnes-Hut node-coverage decision summary

## Validation Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1401_v1_5_standalone_correctness_matrix_test \
  tests.goal1400_v1_5_standalone_app_classification_test \
  tests.goal1398_v1_5_standalone_release_gate_test
```
