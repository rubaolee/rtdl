# Goal 279 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 279 produced the first live bounded RTDL-vs-cuNSearch comparison on real KITTI data.

## What Changed

- added reproducible Linux driver script:
  - `scripts/goal279_kitti_live_real.py`
- used bounded manifests and point packages from the real KITTI raw source tree:
  - `/home/lestat/data/kitti_raw`

## Live Run

Exact bounded settings:

- query start index: `0`
- search start index: `1`
- max frames per package: `1`
- max points per frame: `64`
- max total points: `64`
- radius: `1.0`
- `k_max`: `1`

Live artifacts on Linux:

- clean repo clone:
  - `/home/lestat/work/rtdl_v05_live_clean`
- comparison report:
  - `/home/lestat/work/rtdl_v05_live_clean/build/goal279_kitti_live_real/comparison_report.json`

Observed result:

- `query_point_count = 64`
- `search_point_count = 64`
- `reference_row_count = 29`
- `external_row_count = 29`
- `parity_ok = true`

## Important Boundary

The first attempt used the same point package on both sides and exposed a semantic mismatch:

- RTDL reference includes exact self-matches
- cuNSearch live comparison path does not return those exact self-matches for identical query/search point sets

That run was not treated as the closure result. The closed result uses consecutive real KITTI frames, which is the more honest real-data comparison shape anyway.

## Result

Goal 279 is complete. RTDL now has a real bounded Linux parity result against cuNSearch on official KITTI raw data.
