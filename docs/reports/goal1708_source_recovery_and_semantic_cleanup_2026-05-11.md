# Goal1708 Source Recovery and Semantic Cleanup

Date: 2026-05-11

Status: local recovery follow-up after Goal1705/Goal1707.

## Context

Goal1707 reported that local source synchronization had truncated the Embree
native files during the pod validation attempt:

- `src/native/embree/rtdl_embree_api.cpp`
- `src/native/embree/rtdl_embree_prelude.h`

This recovery restored those files from `git HEAD`, replayed the app-agnostic
native renames through Goal1705, and then removed the stale replay artifacts
that the restoration surfaced.

## Fixes

- Recovered the Embree API and prelude tails so the API again reaches
  `rtdl_embree_free_rows` and the prelude again closes `extern "C"`.
- Removed stale `db_copy_dataset_table` helper names in Embree, OptiX, and
  Vulkan prepared payload paths.
- Replaced stale `"DB columnar inputs must not be null"` messages with
  payload-field wording.
- Repaired OptiX/Vulkan columnar payload validation and copy code that had been
  partially replayed to `fields` while still referencing a stale `columns`
  local.
- Replaced graph traversal `field_index_count` replay artifacts with
  `edge_index_count` across native graph backends.

## Current Verification

The following focused checks pass locally:

```text
py -3 -m unittest tests.goal1704_legacy_purity_symbol_cleanup_test \
  tests.goal1699_db_to_columnar_payload_native_migration_test \
  tests.goal1680_current_native_app_leakage_gap_test \
  tests.goal1658_python_rtdl_product_checkpoint_test -q

py -3 -m unittest tests.goal1699_db_to_columnar_payload_native_migration_test \
  tests.goal1697_polygon_to_shape_native_migration_test \
  tests.goal1695_knn_to_k_closest_hits_native_migration_test \
  tests.goal1690_apple_rt_bfs_to_frontier_discover_migration_test \
  tests.goal1688_bfs_to_frontier_edge_traversal_native_migration_test \
  tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test \
  tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test \
  tests.goal1672_native_app_leakage_migration_classification_test \
  tests.goal1676_native_leakage_delta_regression_test \
  tests.goal1668_native_engine_app_agnostic_directive_test \
  tests.goal1675_partner_protocol_substrate_test -q
```

The stale-native scan now reports zero hits for:

- `db_copy_dataset_table`
- `DB columnar inputs must not be null`
- `field_index_count`
- the six legacy exported ABI names from Goal1704

The purity audit still reports no legacy customized native symbols while keeping
`pure_native_app_contract_ready` false until the remaining false-positive
classification, distinct-AI review, and pod/hardware execution evidence are
recorded.

## Boundary

`tests.goal903_embree_graph_ray_traversal_test` still cannot complete in this
local environment because the Oracle native library build fails in the Windows
SDK/UCRT toolchain headers while preparing CPU/oracle summaries. The observed
failure is a local toolchain build failure, not a new app-shaped native ABI hit.

The release wording remains blocked:

```text
RTDL native internals are fully app-agnostic.
```

