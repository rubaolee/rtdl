# Goal1304: v1.5 Generic Migration Inventory

Date: 2026-05-05

## Purpose

Goal1304 records the current internal v1.5 migration state after Goals
1297-1303. The aim is to prevent the project from losing track of which
app-specific continuations have moved to generic primitives and which remain
intentionally deferred.

This is not a public release gate and does not authorize public NVIDIA speedup
wording.

## Machine-Readable Gate

Added:

```text
src/rtdsl/v1_5_migration_inventory.py
```

Exported APIs:

```text
v1_5_generic_migration_inventory()
validate_v1_5_generic_migration_inventory()
v1_5_generic_migration_blockers()
```

## Completed Generic Rows

| Goal | App | Subpath | Generic primitive | Summary primitive |
| --- | --- | --- | --- | --- |
| Goal1297 | `graph_analytics` | `visibility_edges_reusable_batches` | `ANY_HIT` | `COUNT_HITS` |
| Goal1299 | `service_coverage_gaps` | `gap_summary_prepared` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` |
| Goal1299 | `event_hotspot_screening` | `count_summary_prepared` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` |
| Goal1300 | `ann_candidate_search` | `candidate_threshold_prepared` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` |
| Goal1300 | `facility_knn_assignment` | `coverage_threshold_prepared` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` |
| Goal1301 | `outlier_detection` | `density_count` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` |
| Goal1301 | `dbscan_clustering` | `core_count` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` |
| Goal1302 | `barnes_hut_force_app` | `node_coverage_prepared` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` |
| Goal1302 | `hausdorff_distance` | `directed_threshold_prepared` | `FIXED_RADIUS_COUNT_THRESHOLD_2D` | `REDUCE_INT(COUNT)` |
| Goal1303 | `robot_collision_screening` | `prepared_count` | `ANY_HIT` | `COUNT_HITS` |

## Deferred Rows

| App | Subpath | Status | What unblocks it |
| --- | --- | --- | --- |
| `robot_collision_screening` | `prepared_pose_flags` | `deferred_app_specific` | Define a grouped boolean reduction ABI. |
| `database_analytics` | `sales_risk_compact_summary` | `deferred_app_specific` | Define generic grouped integer `COUNT/SUM` wrappers for numeric predicate lowering. |
| `polygon_pair_overlap_area_rows` | `candidate_discovery_and_exact_area` | `deferred_app_specific` | Define reviewed `REDUCE_FLOAT(SUM)` tolerance/result-shape contract for exact area aggregation. |
| `polygon_set_jaccard` | `chunked_candidate_scoring` | `diagnostic_blocked` | Define `COLLECT_K_BOUNDED` overflow behavior and scoring reduction, then prove correctness/performance; current status remains slower/diagnostic. |

## Guardrails

- Active v1.5 backend scope is Embree and OptiX only.
- Vulkan, HIPRT, and Apple RT remain frozen before v2.1.
- Every row has `public_wording_authorized=false`.
- Pod evidence remains internal migration evidence unless exact-subpath public
  wording receives separate review and 3-AI consensus.

## Verification

Passed locally:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1304_v1_5_generic_migration_inventory_test
```

The broader next gate should include Goal1298-Goal1304 focused tests.
