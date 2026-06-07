# Goal3771 HIPRT Fixed-Radius Ranked-Summary Aggregate

Date: 2026-06-07

## Purpose

Goal3771 adds a generic HIPRT prepared fixed-radius ranked-summary aggregate for
3D point workloads. It mirrors the existing OptiX aggregate contract at the
prepared-handle level:

- `query_count`
- `bounded_neighbor_count`
- `nearest_id_checksum`
- `kth_id_checksum`
- `sum_distance`

The new native symbol is:

`rtdl_hiprt_aggregate_prepared_fixed_radius_ranked_summary_3d`

The Python-facing method is:

`PreparedHiprtFixedRadiusNeighbors3D.aggregate_ranked_summary(query_points, k_max=...)`

## Implementation

- Added `RtdlFixedRadiusRankedNeighborAggregate` to the HIPRT host ABI.
- Added `RtdlFixedRadiusRankedSummaryAggregate3DKernel`.
- Added a lazy prepared-handle aggregate kernel.
- Added a C ABI wrapper and Python ctypes binding.
- Added `fixed_radius_ranked_summary_aggregate_3d` to the engine feature matrix.
- Updated the v2.10 AMD/HIPRT parity matrix so `rtnn` no longer lists
  `ranked_summary_aggregate` as a missing generic HIPRT contract.

## Boundary

This closes only the ranked-summary aggregate part of the RTNN HIPRT gap. RTNN
still needs the heavier batched prepared-query sweep,
`batched_prepared_query_sweep`, before the benchmark row can move to
`ready_for_amd_functional_pod`.

Any validation on the current pod is HIPRT through CUDA/Orochi on NVIDIA
hardware. That is useful functional evidence for the HIPRT code path, but it is
not AMD hardware evidence and does not authorize release, AMD performance,
broad RT-core, whole-app speedup, paper reproduction, or public benchmark
claims.

## Evidence

Artifact:

`docs/reports/goal3771_hiprt_fixed_radius_ranked_aggregate_a5000.json`

Environment:

- GPU: NVIDIA RTX A5000
- Source commit: `38fa119c`
- Scoped source dirty: `false`
- HIPRT SDK: `/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54`
- Backend route: HIPRT through CUDA/Orochi on NVIDIA hardware

Portable local validation passed before pod evidence:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal3771_hiprt_fixed_radius_ranked_aggregate_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Result:

- 14 tests passed.
- 1 local native-HIPRT test skipped because the Windows library was not loaded.

Clean pod validation from `/root/rtdl_goal3771_clean`:

```text
make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3771_hiprt_fixed_radius_ranked_aggregate_test \
  tests.goal3769_hiprt_fixed_radius_threshold_flags_test \
  tests.goal3753_amd_hiprt_benchmark_parity_plan_test
```

Result:

- 19 tests passed.
- 0 tests skipped.
- The clean source commit was `38fa119c`.
- The scoped source status was clean.

Correctness sample:

- Points: `4`
- `k_max`: `3`
- Prepared row count: `10`
- Row-path aggregate matched HIPRT aggregate for integer fields.
- `sum_distance` absolute error: `0.0`
- HIPRT aggregate:
  `query_count=4`, `bounded_neighbor_count=10`, `nearest_id_checksum=10`,
  `kth_id_checksum=11`, `sum_distance=1.600000023841858`

## Parity Position

After Goal3771, the `rtnn` HIPRT row no longer lists
`ranked_summary_aggregate` as missing. It remains in
`needs_generic_hiprt_extension` because `batched_prepared_query_sweep` is still
missing.
