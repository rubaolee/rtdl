# Goal845 Robot Baseline Iteration Contract Adjustment

## Scope

Adjust the active robot baseline contract so the large exact CPU oracle remains correctness-credible and operationally collectable under Goal836.

## Problem

The active robot row in the Goal759/Goal835 chain used this scale:

- `pose_count=200000`
- `obstacle_count=1024`
- `iterations=10`

That scale was defensible for a lightweight summary benchmark, but it is not operationally reasonable for the exact CPU oracle collector used by Goal835:

- the robot CPU oracle performs exact any-hit validation over the full large-scale case
- even after the Linux-only Goal844 parallelization, one exact repeat still takes on the order of minutes
- Goal836 only requires `minimum_repeated_runs=3`
- keeping `iterations=10` in the contract forces the baseline artifact to encode a heavier repeat policy than the release gate actually needs

This made the active robot CPU baseline a contract-level bottleneck rather than a tooling gap.

## Decision

Keep the semantic workload scale intact:

- `pose_count=200000`
- `obstacle_count=1024`

Reduce only the active robot baseline iteration policy:

- from `iterations=10`
- to `iterations=3`

## Why This Is Correct

- The artifact remains large-scale and same-semantics.
- The change aligns the stored `benchmark_scale` with Goal836's explicit minimum review rule instead of silently over-collecting.
- The change does not relax correctness parity, phase separation, or same-semantics matching.
- The change does not authorize any new RTX speedup claim.

## What Changed

- `scripts/goal759_rtx_cloud_benchmark_manifest.py`
  - robot `prepared_pose_flags` scale now uses `iterations=3`
- `tests/goal835_rtx_baseline_collection_plan_test.py`
  - updated expected robot scale
- `tests/goal837_baseline_scale_identity_hardening_test.py`
  - updated expected robot scale
- regenerated derived artifacts:
  - `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`
  - `docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.json`
  - `docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.generated.md`
  - `docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.json`
  - `docs/reports/goal838_local_baseline_collection_manifest_2026-04-23.generated.md`
  - `docs/reports/goal843_linux_active_baseline_batch_plan_2026-04-23.json`
  - `docs/reports/goal843_linux_active_baseline_batch_plan_2026-04-23.md`
  - `docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.json`
  - `docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.generated.md`

## Verification

- `PYTHONPATH=src:. python3 -m unittest -v tests.goal759_rtx_cloud_benchmark_manifest_test tests.goal835_rtx_baseline_collection_plan_test tests.goal837_baseline_scale_identity_hardening_test tests.goal838_local_baseline_collection_manifest_test tests.goal843_linux_active_baseline_batch_test`

Result: `25` focused tests passed.

## Current Honest State

- The two PostgreSQL DB baseline artifacts copied from Linux are now valid under Goal836.
- The copied robot Embree artifact is now intentionally stale because it still encodes `iterations=10`.
- The robot CPU artifact is still missing.

## Boundary

This goal changes the baseline contract for one active robot row. It does not collect the refreshed robot artifacts and does not authorize any RTX speedup claim.
