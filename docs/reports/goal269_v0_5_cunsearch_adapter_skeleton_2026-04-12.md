# Goal 269 Report: v0.5 cuNSearch Adapter Skeleton

Date: 2026-04-12
Status: implemented

## Purpose

Add the first real external baseline adapter skeleton for the prioritized
RTNN comparison library, `cuNSearch`.

## What Landed

### New module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_cunsearch.py`

Added:

- `CuNSearchAdapterConfig`
- `CuNSearchInvocationPlan`
- `resolve_cunsearch_binary(...)`
- `cunsearch_available(...)`
- `cunsearch_adapter_config(...)`
- `plan_cunsearch_fixed_radius_neighbors(...)`
- `write_cunsearch_fixed_radius_request(...)`

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported the adapter config, plan, and request-writer helpers.

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal269_v0_5_cunsearch_adapter_skeleton_test.py`

The test slice verifies:

- explicit binary-path resolution
- honest missing-binary failure
- concrete JSON request contract generation
- config reporting when the adapter is still unconfigured

## Linux Build Note

The current skeleton assumes the first real `cuNSearch` bring-up will happen on
the Linux validation host via:

- `RTDL_CUNSEARCH_BIN`
- optional `RTDL_CUNSEARCH_SOURCE_ROOT`
- optional `RTDL_CUNSEARCH_BUILD_DIR`

This keeps the adapter contract explicit without claiming that the build recipe
or execution protocol is already closed.

## Honesty Boundary

This goal does not claim:

- `cuNSearch` execution is online
- row parity exists
- a reproducible third-party build is complete

It only establishes the first real adapter contract and request payload surface.
