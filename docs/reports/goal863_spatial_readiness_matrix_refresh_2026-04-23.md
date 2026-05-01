# Goal863: Spatial Readiness Matrix Refresh

Date: 2026-04-23

## Purpose

Refresh the canonical OptiX readiness state for `service_coverage_gaps` and
`event_hotspot_screening` after Goals 859-862 completed the local
phase-contract and required same-semantics baseline work.

## Problem

The repo still classified both spatial prepared-summary apps as
`needs_phase_contract`, even though Goal860 already proved the current blocker
is narrower: local baseline work is complete and only real RTX OptiX artifacts
are still missing.

That drift showed up in:

- `src/rtdsl/app_support_matrix.py`
- `docs/app_engine_support_matrix.md`
- `scripts/goal849_spatial_promotion_packet.py`
- tests and generated packets that still asserted `needs_phase_contract`

## Change

Added the explicit readiness state `needs_real_rtx_artifact` and moved both
spatial prepared-summary apps into it.

Updated the support matrix text so the blocker is stated precisely:

- local dry-run and same-semantics baselines are complete
- promotion now requires real RTX OptiX artifacts and review

Updated the spatial promotion packet to reflect the new state and the current
handoff point:

- local packet is complete
- next step is the Goal862-focused RTX artifact run

## Files

- `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`
- `/Users/rl2025/rtdl_python_only/docs/app_engine_support_matrix.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
- `/Users/rl2025/rtdl_python_only/scripts/goal849_spatial_promotion_packet.py`
- `/Users/rl2025/rtdl_python_only/tests/goal705_optix_app_benchmark_readiness_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal759_rtx_cloud_benchmark_manifest_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal819_spatial_prepared_summary_rt_core_gate_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal822_rtx_cloud_manifest_claim_boundary_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal849_spatial_promotion_packet_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal848_v1_0_rt_core_goal_series_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal849_spatial_promotion_packet_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal849_spatial_promotion_packet_2026-04-23.md`

## Verification

- Focused tests:
  - `tests.goal705_optix_app_benchmark_readiness_test`
  - `tests.goal759_rtx_cloud_benchmark_manifest_test`
  - `tests.goal819_spatial_prepared_summary_rt_core_gate_test`
  - `tests.goal822_rtx_cloud_manifest_claim_boundary_test`
  - `tests.goal849_spatial_promotion_packet_test`
  - `tests.goal860_spatial_partial_ready_gate_test`
  - `tests.goal862_spatial_rtx_collection_packet_test`
- Result: `34` tests, `OK`
- `py_compile` passed for touched Python files
- `git diff --check` passed

## Boundary

This change does not promote either app to `ready_for_rtx_claim_review`.

It only makes the repo state truthful:

- `service_coverage_gaps` and `event_hotspot_screening` remain
  `rt_core_partial_ready`
- their current OptiX benchmark-readiness blocker is
  `needs_real_rtx_artifact`
- real RTX artifacts are still required before any promotion or claim review
