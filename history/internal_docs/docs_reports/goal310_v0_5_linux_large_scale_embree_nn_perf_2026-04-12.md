# Goal 310 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Primary validation platform: `Linux (lestat-lx1)`

## Summary

Goal 310 closes the first honest Linux large-scale Embree performance slice for
the v0.5 3D nearest-neighbor line.

The benchmark uses:

- duplicate-free KITTI raw point packages
- `16384` points in the query package
- `16384` points in the search package
- real Linux Embree `4.3.0`
- parity against the native CPU/oracle path

The most important result is:

- Embree is clearly faster than the native CPU/oracle path for:
  - 3D `fixed_radius_neighbors`
  - 3D `bounded_knn_rows`
- Embree 3D `knn_rows` exposed a real performance defect at this scale
- that defect was fixed by shrinking the Embree KNN query radius once the
  current top-`k` set is full instead of collecting and sorting the entire
  candidate set
- after the fix, parity stayed clean and the large Linux KNN time dropped from
  about `45.68 s` to about `18.86 s`

## Code Changes

New benchmark script:

- `scripts/goal301_kitti_embree_vs_native_oracle.py`

Embree backend optimization:

- `src/native/embree/rtdl_embree_scene.cpp`
- `src/native/embree/rtdl_embree_api.cpp`

Sequence update:

- `docs/reports/v0_5_goal_sequence_2026-04-11.md`

## What Changed Technically

The new Linux benchmark script:

- reuses the duplicate-free KITTI pair selector
- writes bounded point packages
- times native CPU/oracle medians separately from prepared Embree timings
- records:
  - prepare-kernel cost
  - point packing cost
  - bind cost
  - first-run cost
  - hot median cost

The Embree KNN optimization changed the backend from:

- infinite-radius point query
- collect every candidate for each query point
- sort the full candidate set

to:

- maintain only the current best `k` rows per query
- replace the current worst row only when a better candidate appears
- shrink `RTCPointQuery.radius` to the current worst accepted distance once the
  working set is full

That keeps the parity semantics but restores the main pruning advantage of the
Embree point-query path.

## Linux Results

Dataset shape:

- source root: `/home/lestat/data/kitti_raw`
- query sequence/frame: `2011_09_26_drive_0001_sync` / `0000000000`
- search sequence/frame: `2011_09_26_drive_0001_sync` / `0000000011`
- duplicate match count: `0`
- repeats: `3`

### Before the KNN Optimization

- `fixed_radius_neighbors`
  - native median: `0.460070 s`
  - Embree hot median: `0.144071 s`
  - parity: `true`
- `bounded_knn_rows`
  - native median: `0.478898 s`
  - Embree hot median: `0.225170 s`
  - parity: `true`
- `knn_rows`
  - native median: `13.630734 s`
  - Embree hot median: `45.679117 s`
  - parity: `true`

### After the KNN Optimization

- `fixed_radius_neighbors`
  - native median: `0.456193 s`
  - Embree hot median: `0.144591 s`
  - parity: `true`
- `bounded_knn_rows`
  - native median: `0.478540 s`
  - Embree hot median: `0.224777 s`
  - parity: `true`
- `knn_rows`
  - native median: `13.604190 s`
  - Embree hot median: `18.862430 s`
  - parity: `true`

## Verification

Focused Embree regression after the optimization:

- `python3 -m unittest tests.goal298_v0_5_embree_3d_fixed_radius_test tests.goal299_v0_5_embree_3d_bounded_knn_test tests.goal300_v0_5_embree_3d_knn_test`
  - `Ran 10 tests`
  - `OK`

Broader regression:

- `python3 -m unittest tests.claude_v0_5_full_review_test`
  - `Ran 112 tests`
  - `OK`

Linux benchmark runs:

- clean Linux checkout under `/home/lestat/work/rtdl_v05_perf`
- benchmark script:
  - `PYTHONPATH=src:. python3 scripts/goal301_kitti_embree_vs_native_oracle.py /home/lestat/data/kitti_raw --point-counts 16384 --repeats 3 --output-dir build/goal301_kitti_embree_vs_native_oracle_16384`
- rerun after optimization:
  - `PYTHONPATH=src:. python3 scripts/goal301_kitti_embree_vs_native_oracle.py /home/lestat/data/kitti_raw --point-counts 16384 --repeats 3 --output-dir build/goal301_kitti_embree_vs_native_oracle_16384_opt`

## Honest Read

Goal 310 is a real Linux large-scale backend performance slice, but it is not a
full cross-platform Embree performance closure.

What is now true:

- Linux large-scale Embree performance is measured on real KITTI data
- parity is clean against the native CPU/oracle path at the measured scale
- Embree is already stronger than native CPU/oracle for:
  - fixed-radius
  - bounded-KNN
- the first large-scale Embree KNN performance defect was found and materially
  improved

What is not being claimed:

- Windows Embree large-scale closure
- macOS large-scale closure
- final Embree optimization completeness
- GPU/backend closure beyond Embree

So the next correct move after Goal 310 is:

- continue optimizing the Embree 3D `knn_rows` path on Linux
- then extend the large-scale performance closure to Windows
