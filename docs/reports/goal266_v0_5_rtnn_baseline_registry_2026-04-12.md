# Goal 266 Report: v0.5 RTNN Baseline Registry

Date: 2026-04-12
Status: implemented

## Purpose

Add a concrete RTNN baseline-library registry and first adapter-decision layer
so the `v0.5` line stops treating comparison libraries as vague future names.

## What Landed

### New module

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/rtnn_baselines.py`

Added:

- `RtnnBaselineLibrary`
- `RtnnBaselineDecision`
- `RTNN_BASELINE_LIBRARIES`
- `RTNN_BASELINE_DECISIONS`
- `rtnn_baseline_libraries(...)`
- `rtnn_baseline_decisions(...)`

### Public surface

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`

Exported the new RTNN baseline registry types and query helpers.

### Tests

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal266_v0_5_rtnn_baseline_registry_test.py`

The test slice verifies:

- the RTNN paper comparison-set libraries are present
- existing repo baselines remain labeled as bounded/non-paper-set paths
- `cuNSearch` is currently the prioritized first adapter
- `PCLOctree` is explicitly marked as higher-friction and deferred
- all paper-set libraries remain 3D-targeted

## Honesty Boundary

This goal does not claim:

- any third-party baseline adapter is online
- any package/build recipe is complete
- any paper comparison is executable today

It only makes the baseline scope and adapter decisions explicit.
