# Goal2553: Native App-Term Purity Gate

Date: 2026-05-23
Status: implemented as an internal engine-purity slice

## Context

Goal2551 consensus identified native app-knowledge leakage in the active
Embree/OptiX engine sources. The clearest non-ABI case was the internal
`DbScan` / `db_scan` naming around the columnar predicate-scan traversal path.

The Goal2552 capacity-overflow fix handled a correctness contract issue first.
This Goal2553 slice handles the next low-risk engine-purity issue without
renaming public compatibility structs.

## Change

The active Embree/OptiX internal predicate-scan implementation now uses generic
names:

- OptiX `kDbScanKernelSrc` -> `kColumnarPredicateScanKernelSrc`
- OptiX `DbScanParams` -> `ColumnarPredicateScanParams`
- OptiX `DbScanLaunchParams` -> `ColumnarPredicateScanLaunchParams`
- OptiX `DbScanPipeline` / `g_dbscan` -> `ColumnarPredicateScanPipeline` /
  `g_columnar_predicate_scan`
- OptiX `db_scan_kernel.cu` -> `columnar_predicate_scan_kernel.cu`
- OptiX `__raygen__/__miss__/__intersection__/__anyhit__db_scan_*` ->
  `columnar_predicate_scan_*`
- Embree `kDbScanRay` and `DbScanRayQueryState` ->
  `kColumnarPredicateScanRay` and `ColumnarPredicateScanRayQueryState`

A reusable source gate was added:

```bash
PYTHONPATH=src:. python scripts/goal2553_native_engine_purity_gate.py
```

The gate scans active Embree/OptiX native sources for benchmark/app terms:
`dbscan`, `raydb`, `robot`, `collision`, `barnes`, `inverse_square`, and
standalone `force`, with false-positive allowances for CUDA `__forceinline__`
and generic "brute-force" comments.

## Boundary

This does not rename the public `RtdlDb*` ABI, compatibility C symbols, Python
`db_*` user-facing modes, historical reports, or inactive pre-v2.1 native
surfaces such as Vulkan/HIPRT/Apple RT.

The remaining P0 migration is the larger public/native ABI naming cleanup:
`RtdlDbField`, `RtdlDbScalar`, `RtdlDbClause`, `RtdlDbGrouped*Row`, and related
compatibility symbols need a staged alias/deprecation strategy before external
ABI stabilization.

## Validation

Focused local validation:

```bash
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
  tests.goal2553_native_engine_purity_gate_test \
  tests.goal2552_grouped_capacity_overflow_contract_test \
  tests.goal2551_benchmark_app_wave_rethinking_consensus_test
```

Result: 11 tests passed for the initial focused set; 35 tests passed after
adding the existing grouped-capacity and RayDB-style source-contract tests.

Native GPU validation is still required before claiming runtime behavior for
the renamed OptiX pipeline on an NVIDIA system.
