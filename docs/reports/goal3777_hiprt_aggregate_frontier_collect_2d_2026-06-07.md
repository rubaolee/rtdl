# Goal3777 HIPRT Aggregate-Frontier Collect 2D

## Purpose

Goal3777 closes the generic HIPRT row-collection side of the Barnes-Hut parity
gap without putting Barnes-Hut force math into the native engine.

The new native ABI is:

`rtdl_hiprt_collect_aggregate_frontier_2d`

It matches the existing Embree and OptiX app-agnostic aggregate-frontier ABI:
input source rows, aggregate-tree rows, child/member CSR, `theta`, capacity
limits, and fail-closed overflow outputs. The output is only the generic
seven-column i64 frontier row schema:

`source_id`, `frontier_kind_code`, `item_id`, `owner_aggregate_id`,
`dfs_index`, `resume_index`, `metadata_flags`.

## What Changed

- Added `RtdlAggregateFrontierSource2D` and `RtdlAggregateFrontierNode2D` to the
  HIPRT native prelude.
- Added the HIPRT host-native aggregate-frontier row collector in
  `src/native/hiprt/rtdl_hiprt_api.cpp`.
- Added `rtdsl.collect_aggregate_frontier_2d_hiprt`.
- Added `aggregate_frontier_collect_2d` to the engine feature matrix with
  HIPRT status `native`.
- Updated the aggregate-frontier native ABI contract and lowering plan to list
  Embree, OptiX, and HIPRT implementations.
- Updated the v2.10 AMD/HIPRT parity map so `barnes_hut` no longer lists
  `hierarchical_node_coverage_summary` as missing. It still lists
  `grouped_vector_force_reduction` as missing.
- Regenerated `docs/rtdl_primitive_catalog.md` from
  `src/rtdsl/primitive_hierarchy.py`.

## Barnes-Hut Impact

This narrows the Barnes-Hut HIPRT gap, but it does not close it.

Closed by Goal3777:

- generic aggregate-frontier / hierarchical node-coverage row collection;
- HIPRT symbol parity with the Embree/OptiX aggregate-frontier ABI;
- fail-closed bounded row materialization for this frontier contract.

Still open:

- grouped vector-force reduction;
- AMD hardware functional validation;
- AMD performance evidence;
- any public speedup or paper-reproduction wording.

## Validation

Local focused validation passed:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3777_hiprt_aggregate_frontier_collect_2d_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal2639_aggregate_frontier_native_abi_contract_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3090_v2_7_discovery_metadata_backfill_test
```

Broader local HIPRT-parity slice also passed:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3777_hiprt_aggregate_frontier_collect_2d_test tests.goal3776_hiprt_collect_k_bounded_i64_test tests.goal3775_hiprt_ray_triangle_closest_hit_3d_test tests.goal3774_hiprt_point_group_nearest_device_columns_test tests.goal3773_hiprt_point_group_nearest_witness_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal2639_aggregate_frontier_native_abi_contract_test tests.goal2638_aggregate_frontier_collect_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3090_v2_7_discovery_metadata_backfill_test
```

Result: 77 tests passed, 12 skipped.

Clean pod validation:

- SSH: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000, 580.126.09`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- clean workdir: `/root/rtdl_goal3777_clean_1780850895`
- commit: `3e46c533a6e62669ee58f5054e52617726cfa60e`
- command: `make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- focused pod tests: 43 passed, 3 skipped.
- sample parity: HIPRT rows, row offsets, and source IDs match the CPU
  aggregate-frontier reference.
- overflow behavior: fail-closed, no partial result surfaced.
- scoped source dirty: false.

Pod evidence is recorded in:

`docs/reports/goal3777_hiprt_aggregate_frontier_collect_2d_a5000.json`

## Boundary

Goal3777 does not authorize AMD hardware evidence, AMD performance claims,
RT-core speedup claims, whole-app Barnes-Hut claims, paper reproduction claims,
zero-copy claims, release claims, or app-specific native-engine logic.

The NVIDIA CUDA/Orochi HIPRT path is useful functional implementation evidence,
not AMD hardware evidence.
