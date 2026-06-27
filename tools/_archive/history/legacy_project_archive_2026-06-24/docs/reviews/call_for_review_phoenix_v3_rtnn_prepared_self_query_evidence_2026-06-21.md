# Call For Review: Phoenix V3 RTNN Prepared Self-Query Evidence

Reviewer: external AI reviewer
Date: 2026-06-21

## Review Request

Critically review the Phoenix V3 RTNN prepared self-query evidence packet and the associated implementation boundary.

Primary files:

- `docs/rebuild/v3/phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.json`
- `docs/rebuild/v3/evidence/rtnn_self_query_20260621/old_prepared_query.json`
- `docs/rebuild/v3/evidence/rtnn_self_query_20260621/new_prepared_self_query.json`
- `docs/rebuild/v3/evidence/rtnn_self_query_20260621/cupy_grid_reference.json`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `tests/v3_phoenix_rtnn_self_query_aggregate_test.py`
- `tests/v3_phoenix_rtnn_self_query_evidence_test.py`

## Context

This is Phoenix V3 work, not app-specific RTNN work. RTNN is used as a serious evidence harness for a generic fixed-radius-neighbor primitive.

The implemented generic capability is:

`PreparedOptixFixedRadiusNeighbors3D.aggregate_ranked_summary_self_query_batch(...)`

It reuses the prepared search-side device buffer as the query buffer when the query set is identical to the search set. The runner exposes this through an explicit result mode:

`ranked-summary-aggregate-prepared-self-query-batch-float32`

The old prepared-query path remains available for A/B comparison.

## POD Evidence Summary

Hardware:

- NVIDIA RTX 4000 Ada Generation
- Driver 550.127.05
- Compute capability 8.9

Dataset/contract:

- 1,048,576 3-D points
- radius 0.02
- k=50
- repeat=5
- same fixed-radius ranked-summary aggregate contract

Key results:

- Old prepared-query to new prepared-self-query hot speedup: `2.482x`
- Old prepared-query to new prepared-self-query input-pack reduction: `2.784x`
- Old prepared-query to new prepared-self-query cold+query speedup: `1.883x`
- New prepared-self-query over CuPy grid hot-query speedup: `19.437x`
- New prepared-self-query over CuPy grid cold+query speedup: `1.214x`
- New prepared-self-query over CuPy grid runner-wall speedup: `1.030x`
- Integer signature parity with old prepared-query and CuPy grid: true
- Sum-distance relative error vs CuPy grid: `1.207e-10`

Current packet decision:

- This is a real generic engine optimization.
- It is not M7.
- It does not authorize broad V3-vs-V2, whole-app, or end-to-end speedup wording.
- The `19.437x` number may only be described as hot-query prepared self-query speedup.
- The `1.030x` runner-wall result is too small to call a major V3 performance win.

## Questions For Reviewer

1. Is the implemented self-query path a legitimate generic engine capability rather than RTNN-specific tuning?
2. Is the evidence sufficient to record a real V3 engine optimization?
3. Is the packet correct to block M7 promotion and broad public speedup claims?
4. Are the forbidden shortcuts strong enough to prevent users from being misled by the 19.437x hot-query result?
5. What concrete improvements are required before this can become an M7 row or a user-facing V3 performance claim?

Please return:

- Verdict: ACCEPT, ACCEPT_WITH_CHANGES, or BLOCK
- P0/P1 findings, if any
- Specific wording or engineering changes required
- A short final recommendation
