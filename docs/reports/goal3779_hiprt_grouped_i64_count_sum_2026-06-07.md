# Goal3779 HIPRT Grouped I64 Count/Sum

## Purpose

Goal3779 adds a small generic HIPRT grouped-reduction materializer:

`rtdl_hiprt_grouped_i64_count_sum`

The contract takes dense group ids and one i64 value column, then returns dense
per-group `count` and `sum` arrays. It deliberately does not understand SQL,
tables, predicates, databases, RayDB, or any app-specific query model.

## What Changed

- Added the app-name-free HIPRT native ABI
  `rtdl_hiprt_grouped_i64_count_sum`.
- Added `rtdsl.grouped_i64_count_sum_hiprt`.
- Added the generic engine feature `grouped_i64_count_sum` with HIPRT status
  `native`.
- Added HIPRT to the `reduction.grouped` primitive hierarchy backend list and
  regenerated the public primitive catalog from source.
- Updated the v2.10 AMD/HIPRT parity map so `raydb_style` no longer lists
  `native_hiprt_grouped_i64_count_sum_fastpath` as missing.

## RayDB-Style Impact

This narrows the RayDB-style AMD/HIPRT gap, but it does not close it.

Closed by Goal3779:

- generic dense grouped i64 count/sum materialization;
- HIPRT symbol parity for the grouped aggregation piece;
- fail-closed validation for out-of-range dense group ids.

Still open:

- generic HIPRT columnar predicate scan fastpath
  (`native_hiprt_columnar_predicate_scan_fastpath`);
- AMD hardware functional validation;
- AMD performance evidence;
- any public speedup, RayDB paper-reproduction, or release wording.

The parity stage for `raydb_style` remains
`compatibility_only_not_amd_perf_ready`.

## Validation

Local focused validation passed:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3779_hiprt_grouped_i64_count_sum_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3776_hiprt_collect_k_bounded_i64_test tests.goal3777_hiprt_aggregate_frontier_collect_2d_test tests.goal3073_v2_7_generated_primitive_catalog_test tests.goal3090_v2_7_discovery_metadata_backfill_test
```

Result: 47 tests passed, 8 skipped.

Clean pod validation:

- SSH: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000, 580.126.09`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- clean workdir: `/root/rtdl_goal3779_clean_1780852622`
- commit: `2096656daee9765f94cecc4d506cbcc98d4ece27`
- command: `make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- focused pod tests: 36 passed, 1 skipped.
- sample parity: HIPRT dense counts `(2, 1, 3, 0)` and sums `(13, 7, 8, 0)` match the Python reference.
- scoped source dirty: false.

Pod evidence is recorded in:

`docs/reports/goal3779_hiprt_grouped_i64_count_sum_a5000.json`

## Boundary

Goal3779 does not authorize AMD hardware evidence, AMD performance claims,
RT-core speedup claims, whole-app RayDB claims, paper reproduction claims,
zero-copy claims, release claims, or app-specific native-engine logic.

The NVIDIA CUDA/Orochi HIPRT path is useful functional implementation evidence,
not AMD hardware evidence.
