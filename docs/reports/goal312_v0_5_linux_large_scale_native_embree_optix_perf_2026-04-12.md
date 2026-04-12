# Goal 312 Report: Linux Large-Scale Native vs Embree vs OptiX Performance

Date: 2026-04-12
Status: implemented locally, Linux-measured, pending saved external review

## Purpose

Run the first honest large-scale Linux comparison across RTDL's three current
3D nearest-neighbor backend classes:
- native CPU/oracle
- Embree
- OptiX

## Scope

Platform:
- Linux only
- host: `lestat-lx1`

Dataset:
- official KITTI raw data under `/home/lestat/data/kitti_raw`
- duplicate-free frame pair selected from:
  - sequence `2011_09_26_drive_0001_sync`
  - query frame `0000000000`
  - search frame `0000000011`

Scale:
- `16384 x 16384` points
- `repeats=3`

Workloads:
- `fixed_radius_neighbors`
- `bounded_knn_rows`
- `knn_rows`

## Implementation

Benchmark script:
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal312_kitti_native_embree_optix.py`

Timing model:
- native CPU/oracle:
  - median end-to-end execution time
- Embree:
  - prepare kernel
  - pack inputs
  - bind
  - first run
  - hot median
- OptiX:
  - prepare kernel
  - pack inputs
  - bind
  - first run
  - hot median

Parity model:
- native CPU/oracle is the truth/performance baseline
- Embree and OptiX are each compared directly to the native rows

## Linux Result

### fixed_radius_neighbors

- native median:
  - `0.499760 s`
- Embree hot median:
  - `0.155707 s`
- OptiX hot median:
  - `0.021086 s`
- parity:
  - Embree `true`
  - OptiX `true`

### bounded_knn_rows

- native median:
  - `0.524166 s`
- Embree hot median:
  - `0.242003 s`
- OptiX hot median:
  - `0.110671 s`
- parity:
  - Embree `true`
  - OptiX `true`

### knn_rows

- native median:
  - `13.606308 s`
- Embree hot median:
  - `18.833467 s`
- OptiX hot median:
  - `0.131348 s`
- parity:
  - Embree `true`
  - OptiX `true`

## Important Technical Result

The first large-scale OptiX KNN run was not parity-clean.

Observed failure:
- exact host-side recomputation exposed a rank swap on one query
- the GPU-side float32 ordering had preserved the wrong rank after exact
  double-distance reconstruction

Fix applied:
- after exact host-side distance recomputation, the 3D OptiX KNN rows are now
  re-sorted by:
  - `query_id`
  - exact `distance`
  - `neighbor_id`
- `neighbor_rank` is reassigned from that exact order

After that fix:
- OptiX KNN parity at `16384` became `true`

## Honest Read

At this Linux large scale:
- OptiX is the fastest backend on all three measured workloads
- Embree is materially faster than native on:
  - fixed-radius
  - bounded-KNN
- Embree is still slower than native on:
  - full KNN
- OptiX is now parity-clean on the measured large-scale KITTI line

## Verification

Linux commands:
- build:
  - `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`
- focused OptiX 3D parity:
  - `PYTHONPATH=src:. python3 -m unittest tests.goal311_v0_5_optix_3d_nn_test`
  - `Ran 4 tests`
  - `OK`
- large-scale benchmark:
  - `PYTHONPATH=src:. python3 scripts/goal312_kitti_native_embree_optix.py /home/lestat/data/kitti_raw --point-counts 16384 --output-dir build/goal312_kitti_native_embree_optix --repeats 3`

Summary artifact written on Linux:
- `/home/lestat/work/rtdl_v05_perf/build/goal312_kitti_native_embree_optix/summary.json`

## Honesty Boundary

This slice closes only the first Linux large-scale benchmark point.

It does not yet claim:
- Windows large-scale backend closure
- macOS large-scale backend closure
- full cross-platform OptiX maturity
- final backend optimization completeness
