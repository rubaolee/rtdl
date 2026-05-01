# Goal 815: DB RT-Core Claim Gate

Date: 2026-04-23

Status: complete

## Problem

The unified DB app has a real OptiX DB backend: it performs BVH candidate
discovery and native C++ filtering/grouping for bounded DB operations. However,
the app is still classified as `python_interface_dominated` because full output
modes can spend substantial time in Python/ctypes preparation, candidate
copy-back, grouped-row decoding, row materialization, and app summary logic.

That means the app can honestly say that a bounded DB sub-path uses OptiX
traversal, but it cannot broadly claim whole-app DBMS-style RTX speedup.

## Change

Added `--require-rt-core` to:

- `examples/rtdl_database_analytics_app.py`

The flag is intentionally narrow:

```bash
python examples/rtdl_database_analytics_app.py \
  --backend optix \
  --output-mode compact_summary \
  --require-rt-core
```

Allowed:

- `--backend optix`
- `--output-mode compact_summary`

Rejected before backend dispatch:

- non-OptiX backends;
- `full` output mode;
- `summary` output mode.

The app payload now includes:

- `rt_core_accelerated`: true only for the bounded OptiX compact-summary path;
- `rt_core_claim_scope`: partial prepared compact-summary DB traversal only,
  not a broad DBMS or whole-app speedup claim.

## Current DB Status

| Path | Status |
| --- | --- |
| CPU/Python | correctness oracle |
| Embree | CPU BVH/RT-style DB execution |
| OptiX full/summary | real backend work but interface/materialization dominated |
| OptiX compact_summary | bounded partial RT-core claim candidate |
| Vulkan | native backend app surface, not this goal's claim target |

## Verification

Run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal815_db_rt_core_claim_gate_test tests.goal804_db_compact_summary_scan_count_test tests.goal705_optix_app_benchmark_readiness_test tests.goal803_rt_core_app_maturity_contract_test
python3 -m py_compile examples/rtdl_database_analytics_app.py tests/goal815_db_rt_core_claim_gate_test.py
git diff --check
```

Expected result: all tests pass and no whitespace errors.

## Release Boundary

This goal improves claim safety. It does not reclassify DB as
`rt_core_ready`, and it does not authorize any broad DB app speedup claim.
