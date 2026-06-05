# Handoff: Claude Review for Goal3447-3451 RayJoin Relation-Column Chain

Please perform an independent read-only review of the RTDL v2.8 RayJoin relation-column chain on current `main`.

## Scope

Review these goals and artifacts:

- Goal3447: generic resident shape-pair active relation device columns
  - `docs/reports/goal3447_shape_pair_active_relation_device_columns_2026-06-05.md`
  - `docs/reports/goal3447_shape_pair_active_relation_device_columns_pod_2026-06-05.json`
  - `tests/goal3447_shape_pair_active_relation_device_columns_test.py`
- Goal3448: prior Claude review
  - `docs/reviews/goal3448_claude_review_goal3447_shape_pair_relation_device_columns_2026-06-05.md`
- Goal3449: generic grouped-count continuation over relation columns
  - `docs/reports/goal3449_shape_pair_relation_grouped_count_2026-06-05.md`
  - `docs/reports/goal3449_shape_pair_relation_grouped_count_pod_2026-06-05.json`
  - `tests/goal3449_shape_pair_relation_grouped_count_test.py`
- Goal3450: sparse-id content correctness and overflow proof
  - `docs/reports/goal3450_shape_pair_relation_device_column_content_2026-06-05.md`
  - `docs/reports/goal3450_shape_pair_relation_device_column_content_pod_2026-06-05.json`
  - `tests/goal3450_shape_pair_relation_device_column_content_test.py`
- Goal3451: v2.8 runtime gap refresh
  - `docs/reports/goal3451_v2_8_runtime_gap_after_relation_columns_content_2026-06-05.md`
  - `src/rtdsl/v2_8_benchmark_runtime_gap.py`
  - `tests/goal3451_v2_8_runtime_gap_after_relation_columns_content_test.py`

Also inspect the implementation surface:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v2_8_geometry_relation_typed_stream.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`

## Review Questions

1. Is the native/runtime relation-column surface app-agnostic, or did RayJoin/CDB/overlay app logic leak below the app layer?
2. Does Goal3449 really use a generic grouped-count continuation over resident columns, and does the sparse-id capacity fix prevent dense ordinal assumptions?
3. Does Goal3450 close the specific Goal3448 content-correctness gap, including active-pair ids and dependency flags, and does its overflow probe fail closed?
4. Is Goal3451's updated runtime-gap wording accurate: the remaining RayJoin work is exact witnesses, overlay-area continuation, large-scale content-reference oracles, and boundary-witness ownership, not scalar active-count or relation-id residency?
5. Are claim boundaries intact: no v2.8 release, public speedup, broad RT-core, true-zero-copy, RayJoin paper reproduction, RTDL-beats-RayJoin, full overlay, hidden dispatch, or app-specific engine claims?
6. What should be the next engineering target: expose generic geometry payload columns for partner witness/area continuation, add a native bounded witness producer, or another route?

## Validation To Run

```powershell
$env:PYTHONPATH="src;."
py -3 -m unittest `
  tests.goal3451_v2_8_runtime_gap_after_relation_columns_content_test `
  tests.goal3450_shape_pair_relation_device_column_content_test `
  tests.goal3449_shape_pair_relation_grouped_count_test `
  tests.goal3447_shape_pair_active_relation_device_columns_test `
  tests.goal3446_v2_8_runtime_gap_after_rayjoin_active_count_device_default_test
```

## Deliverable

Write the review to:

`docs/reviews/goal3452_claude_review_rayjoin_relation_column_chain_3447_3451_2026-06-05.md`

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`. Please lead with findings and be explicit about any required-before-next-step issues.
