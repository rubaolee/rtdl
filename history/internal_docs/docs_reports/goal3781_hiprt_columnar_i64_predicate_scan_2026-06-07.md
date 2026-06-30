# Goal3781 HIPRT Columnar I64 Predicate Scan

## Purpose

Goal3781 adds a generic HIPRT columnar integer predicate-scan materializer:

`rtdl_hiprt_columnar_i64_predicate_scan`

The contract takes column-major int64 columns plus explicit predicate triples
`(column_index, op, value)`, where `op` is one of `eq`, `ne`, `lt`, `le`, `gt`,
or `ge`. It returns matching dense row ids. This is not SQL, not a DBMS, and not
a RayDB-specific query planner.

## What Changed

- Added the app-name-free HIPRT native ABI
  `rtdl_hiprt_columnar_i64_predicate_scan`.
- Added `rtdsl.columnar_i64_predicate_scan_hiprt`.
- Added the generic engine feature `columnar_i64_predicate_scan` with HIPRT
  status `native`.
- Updated the v2.10 AMD/HIPRT parity map so `raydb_style` no longer lists
  `native_hiprt_columnar_predicate_scan_fastpath` as missing.

## RayDB-Style Impact

This closes the RayDB-style generic HIPRT contract gap for functional AMD pod
planning, but it does not provide AMD hardware evidence.

Closed by Goal3781:

- generic columnar int64 predicate scan;
- HIPRT symbol parity for the predicate-scan piece;
- fail-closed bounded row-id materialization.

Still open:

- AMD hardware functional validation;
- AMD performance evidence;
- any public speedup, RayDB paper-reproduction, or release wording.

The parity stage for `raydb_style` moves to `ready_for_amd_functional_pod`.
The overall AMD/HIPRT parity map now has one compatibility-only app remaining:
`triangle_counting`.

## Validation

Local focused validation passed:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3781_hiprt_columnar_i64_predicate_scan_test tests.goal3753_amd_hiprt_benchmark_parity_plan_test tests.goal3775_hiprt_ray_triangle_closest_hit_3d_test tests.goal3776_hiprt_collect_k_bounded_i64_test tests.goal3777_hiprt_aggregate_frontier_collect_2d_test tests.goal3779_hiprt_grouped_i64_count_sum_test tests.goal3780_hiprt_grouped_vector_sum_f64x2_test
```

Result: 57 tests passed, 14 skipped.

Clean pod validation:

- SSH: `root@69.30.85.203 -p 22057`
- GPU: `NVIDIA RTX A5000, 580.126.09`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- clean workdir: `/root/rtdl_goal3781_clean_1780853952`
- commit: `e8eac8472702b85d546522fa58c9b7db3fde1ed2`
- command: `make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- focused pod tests: 34 passed, 1 skipped.
- sample parity: HIPRT row ids `(3, 5)` match the Python reference.
- scoped source dirty: false.

Pod evidence is recorded in:

`docs/reports/goal3781_hiprt_columnar_i64_predicate_scan_a5000.json`

## Boundary

Goal3781 does not authorize AMD hardware evidence, AMD performance claims,
RT-core speedup claims, whole-app RayDB claims, paper reproduction claims,
zero-copy claims, release claims, SQL/DBMS claims, or app-specific native-engine
logic.

The NVIDIA CUDA/Orochi HIPRT path is useful functional implementation evidence,
not AMD hardware evidence.
