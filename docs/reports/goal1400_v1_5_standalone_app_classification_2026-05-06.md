# Goal 1400 - v1.5 Standalone App Classification

Date: 2026-05-06

## Status

Added an app-level standalone-v1.5 classification matrix.

This closes the `app_migration_classification` gate in the standalone release
gate. It does not close correctness, benchmark, support-maturity, release-doc,
or `COLLECT_K_BOUNDED` promotion gates.

## Classification Classes

The matrix uses six classes:

- `fully_generic`
- `wrapper_backed`
- `scalar_only`
- `collection_dependent`
- `frozen`
- `demo_only`

## Current Counts

Current app count:

- total public apps: `18`
- standalone included: `14`
- standalone excluded: `4`

Excluded from standalone v1.5 unless later gates change:

- `segment_polygon_anyhit_rows`: collection-dependent on `COLLECT_K_BOUNDED`
- `polygon_set_jaccard`: collection-dependent on `COLLECT_K_BOUNDED`
- `apple_rt_demo`: demo-only, frozen from active v1.5 scope
- `hiprt_ray_triangle_hitcount`: frozen before v2.1

Representative included classes:

- `fully_generic`: `service_coverage_gaps`, `event_hotspot_screening`
- `wrapper_backed`: `database_analytics`, `robot_collision_screening`,
  `polygon_pair_overlap_area_rows`
- `scalar_only`: `graph_analytics`, `hausdorff_distance`,
  `ann_candidate_search`, `dbscan_clustering`, `barnes_hut_force_app`

## Release Gate Effect

`validate_v1_5_standalone_release_gate()` now reports:

- `app_migration_classification: true`
- `standalone_included_app_count: 14`
- `standalone_excluded_app_count: 4`

The release remains blocked because the following gates are still false:

- `collect_k_bounded_resolution`
- `same_contract_per_app_correctness`
- `same_contract_per_app_benchmarks`
- `test_backed_support_maturity_matrix`
- `release_docs_and_public_wording`

## Validation

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1400_v1_5_standalone_app_classification_test tests.goal1398_v1_5_standalone_release_gate_test tests.goal1399_collect_k_bounded_resolution_test tests.goal1304_v1_5_generic_migration_inventory_test
```

Result:

```text
Ran 20 tests in 0.004s
OK
```

## Next Work

The next standalone gate is same-contract per-app correctness evidence for the
14 included app surfaces, while keeping the 4 excluded apps out of the release
surface unless `COLLECT_K_BOUNDED` is promoted.

