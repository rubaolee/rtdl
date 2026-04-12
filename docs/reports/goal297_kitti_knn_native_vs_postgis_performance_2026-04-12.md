# Goal 297 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 297 extended the native-versus-PostGIS performance line to 3D `knn_rows`.

The most important result is:

- native RTDL beats PostGIS on the measured duplicate-free KITTI 3D KNN line
- native RTDL remains parity-clean against the Python truth path
- PostGIS remains parity-clean against the Python truth path
- the PostGIS path is being used here as a 3D KNN correctness/performance anchor,
  not as an indexed 3D KNN acceleration claim

## Baseline Scope

The external anchor in this goal is an additive 3D PostGIS KNN baseline using:

- `geometry(PointZ, 0)`
- `gist_geometry_ops_nd` table indexes for consistency with the 3D point surface
- `ST_3DDistance(...)`
- per-query `CROSS JOIN LATERAL` ranking with `ROW_NUMBER()`

Important boundary:

- unlike the earlier 2D PostGIS KNN path, this 3D path does **not** claim a
  dedicated indexed 3D KNN operator
- the query is a bounded correctness anchor for RTDL's 3D KNN contract, not a
  claim that PostGIS is providing specialized 3D nearest-neighbor acceleration

## Results

Parameters:

- `k = 4`
- duplicate-free KITTI frame pairs
- `repeats = 3`

### 512 points

- RTDL Python reference:
  - `0.110261 s`
- RTDL native oracle:
  - `0.010135 s`
- PostGIS 3D KNN:
  - `0.110395 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

### 1024 points

- RTDL Python reference:
  - `0.477471 s`
- RTDL native oracle:
  - `0.040259 s`
- PostGIS 3D KNN:
  - `0.454095 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

### 2048 points

- RTDL Python reference:
  - `2.276123 s`
- RTDL native oracle:
  - `0.162865 s`
- PostGIS 3D KNN:
  - `1.643621 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

### 4096 points

- RTDL Python reference:
  - `9.593832 s`
- RTDL native oracle:
  - `0.700151 s`
- PostGIS 3D KNN:
  - `6.525603 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

### 8192 points

- RTDL Python reference:
  - `40.743128 s`
- RTDL native oracle:
  - `3.097389 s`
- PostGIS 3D KNN:
  - `26.474065 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

## Honest Read

- Goal 296 made native 3D `knn_rows` real
- Goal 297 shows that this path is both correct and materially faster than the
  PostGIS 3D KNN anchor on the measured duplicate-free KITTI line
- native RTDL beats PostGIS from `512` through `8192` points on this workload
- the Python truth path remains the correctness oracle, but it is no longer the
  relevant implementation-performance story

Useful bounded ratios:

- at `512`, native RTDL is about `10.9x` faster than PostGIS
- at `1024`, native RTDL is about `11.3x` faster than PostGIS
- at `2048`, native RTDL is about `10.1x` faster than PostGIS
- at `4096`, native RTDL is about `9.3x` faster than PostGIS
- at `8192`, native RTDL is about `8.5x` faster than PostGIS

## Boundary

- this is a bounded KITTI 3D `knn_rows` result on the current Linux host
- it does not claim indexed 3D PostGIS KNN acceleration
- it does not claim accelerated 3D RTDL backend closure
- it does not claim broader paper-family superiority beyond the measured
  duplicate-free KITTI KNN cases
