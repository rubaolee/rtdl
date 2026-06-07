# Goal3772 HIPRT Fixed-Radius Ranked Batch Sweep

Date: 2026-06-07

Status: implemented and validated on a clean NVIDIA RTX A5000 CUDA/Orochi HIPRT pod clone.

## Purpose

Goal3771 closed the HIPRT prepared fixed-radius ranked-summary aggregate contract, but the RTNN benchmark parity row still needed a generic batched prepared-query sweep. Goal3772 adds that missing generic contract without introducing RTNN-specific native engine logic.

## What Changed

- Added `rtdl_hiprt_aggregate_prepared_fixed_radius_ranked_summary_batch_3d`.
- Added `PreparedHiprtFixedRadiusNeighbors3D.aggregate_ranked_summary_batch(...)`.
- The batch request accepts per-request `radius` and `k_max`.
- The prepared handle stores its maximum prepared radius. Request radii may be equal to or smaller than the prepared radius; larger radii are rejected because the prepared AABB geometry would not be conservative for them.
- Existing single-operation radius overrides now reject mismatched radii instead of silently ignoring them.
- Added feature-matrix entry `fixed_radius_ranked_summary_batched_sweep_3d`.
- Moved the RTNN v2.10 AMD/HIPRT parity row to `ready_for_amd_functional_pod`.

## Boundary

This is still not AMD hardware evidence. The local and A5000 CUDA/Orochi HIPRT route is useful functional evidence, but it does not authorize AMD performance claims, public speedup wording, whole-app acceleration wording, RTDL-beats-paper wording, or release wording.

## Validation Plan

- Local portable tests:
  - `tests.goal3772_hiprt_fixed_radius_ranked_batch_sweep_test`
  - `tests.goal3771_hiprt_fixed_radius_ranked_aggregate_test`
  - `tests.goal3753_amd_hiprt_benchmark_parity_plan_test`
- Pod validation:
  - clean clone at implementation commit `aa3eda9e`
  - `make build-hiprt` passed
  - focused test slice passed: `Ran 22 tests OK`
  - artifact: `docs/reports/goal3772_hiprt_fixed_radius_ranked_batch_sweep_a5000.json`

## Claim Boundary

All release, AMD performance, whole-app speedup, broad RT-core, paper-reproduction, and app-specific native-engine claim flags remain false.
