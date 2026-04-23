# Goal 819: Spatial Prepared-Summary RT-Core Gate

Date: 2026-04-23

Status: complete

## Problem

`service_coverage_gaps` and `event_hotspot_screening` now expose prepared OptiX
summary modes that use fixed-radius traversal and compact outputs. Their row
modes are not the claim paths. Claim-sensitive scripts need a way to require
the prepared traversal modes and reject row mode before cloud runs.

## Change

Added `--require-rt-core` to:

- `examples/rtdl_service_coverage_gaps.py`
- `examples/rtdl_event_hotspot_screening.py`

Accepted claim-sensitive combinations:

```bash
python examples/rtdl_service_coverage_gaps.py \
  --backend optix \
  --optix-summary-mode gap_summary_prepared \
  --require-rt-core

python examples/rtdl_event_hotspot_screening.py \
  --backend optix \
  --optix-summary-mode count_summary_prepared \
  --require-rt-core
```

Rejected before backend dispatch:

- non-OptiX backends under `--require-rt-core`;
- OptiX row mode under `--require-rt-core`.

Payloads now include:

- `optix_performance`
- `rt_core_accelerated`

## Current Status

These apps remain `rt_core_partial_ready`, not `rt_core_ready`, because they
still need phase-clean RTX evidence and review before any public claim.

## Verification

Run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal819_spatial_prepared_summary_rt_core_gate_test tests.goal705_optix_app_benchmark_readiness_test tests.goal803_rt_core_app_maturity_contract_test
python3 -m py_compile examples/rtdl_service_coverage_gaps.py examples/rtdl_event_hotspot_screening.py tests/goal819_spatial_prepared_summary_rt_core_gate_test.py
git diff --check
```

Expected result: all tests pass and no whitespace errors.

## Release Boundary

This goal adds claim gates for already-existing prepared summary modes. It does
not promote the apps to `rt_core_ready` and does not authorize whole-app RTX
speedup claims.
