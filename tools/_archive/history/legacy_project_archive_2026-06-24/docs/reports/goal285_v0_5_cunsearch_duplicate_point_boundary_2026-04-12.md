# Goal 285 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 285 isolated the first strict cuNSearch correctness failure into a minimal real KITTI duplicate-point reproducer.

## Reproducer

Source package:

- `/home/lestat/work/rtdl_v05_live_perf/build/goal284_kitti_three_way_scaling_sweep/points_1024`

Selected points:

- query:
  - `1008`
- search:
  - `1007`
  - `1008`

Radius:

- `1.0`

## Exact Duplicate Audit

The selected probe contains exactly one exact cross-package duplicate:

- query `1008`
- search `1007`

Coordinates:

- `(-21.226999282836914, -13.75100040435791, 1.0640000104904175)`

The nearby non-duplicate search point is:

- search `1008`
- distance to query:
  - `0.08324557843069172`

## Result

Reference rows:

- `{"query_id": 1008, "neighbor_id": 1007, "distance": 0.0}`
- with `k_max = 2`, the reference still orders the exact duplicate first

cuNSearch rows:

- with `k_max = 1`:
  - `{"query_id": 1008, "neighbor_id": 1008, "distance": 0.08324557843069172}`
- with `k_max = 2`:
  - still only
    - `{"query_id": 1008, "neighbor_id": 1008, "distance": 0.08324557843069172}`

## Honest Read

- the current cuNSearch mismatch is not broad random drift
- it reproduces in a tiny real-data case centered on an exact cross-package duplicate point
- on the current live path, cuNSearch does not return the exact duplicate neighbor in this case
- raising `k_max` from `1` to `2` does not recover the duplicate row

What remains unknown:

- whether this is intrinsic cuNSearch behavior for duplicate points
- whether RTDL can mitigate it honestly without distorting the benchmark contract
