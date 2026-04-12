# Goal 295 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 295 extended the native-versus-PostGIS performance line to 3D
`bounded_knn_rows`.

The most important result is:

- native RTDL beats PostGIS on the measured duplicate-free KITTI 3D
  bounded-KNN line
- native RTDL remains parity-clean against the Python truth path
- PostGIS remains parity-clean against the Python truth path
- the benchmark stays inside the honest boundary of RTDL's current 3D
  bounded-radius KNN contract

## Baseline Scope

The external anchor in this goal is a new additive 3D PostGIS bounded-KNN
baseline using:

- `geometry(PointZ, 0)`
- `gist_geometry_ops_nd`
- `ST_3DDWithin(...)`
- `ST_3DDistance(...)`
- per-query `ROW_NUMBER()` ranking bounded by the requested radius and `k_max`

This is intentionally a bounded-radius ranked-neighbor baseline, not a claim of
generic 3D PostGIS KNN acceleration semantics beyond the RTDL contract.

## Results

Parameters:

- `radius = 1.0`
- `k_max = 4`
- duplicate-free KITTI frame pairs
- `repeats = 3`

### 512 points

- RTDL Python reference:
  - `0.057716 s`
- RTDL native oracle:
  - `0.003240 s`
- PostGIS 3D bounded-KNN:
  - `0.012475 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

### 1024 points

- RTDL Python reference:
  - `0.223452 s`
- RTDL native oracle:
  - `0.005826 s`
- PostGIS 3D bounded-KNN:
  - `0.019669 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

### 2048 points

- RTDL Python reference:
  - `0.890511 s`
- RTDL native oracle:
  - `0.016441 s`
- PostGIS 3D bounded-KNN:
  - `0.054882 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

### 4096 points

- RTDL Python reference:
  - `3.557861 s`
- RTDL native oracle:
  - `0.051250 s`
- PostGIS 3D bounded-KNN:
  - `0.223965 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

### 8192 points

- RTDL Python reference:
  - `14.186350 s`
- RTDL native oracle:
  - `0.177445 s`
- PostGIS 3D bounded-KNN:
  - `0.851509 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`

## Honest Read

- Goal 293 made native 3D `bounded_knn_rows` real
- Goal 295 shows that this path is not only correct but materially faster than
  the PostGIS bounded-KNN anchor on the measured KITTI line
- native RTDL beats PostGIS from `512` through `8192` points on this workload
- the Python truth path is still the correctness oracle, but it is no longer
  the relevant implementation-performance story

Useful bounded ratios:

- at `512`, native RTDL is about `3.9x` faster than PostGIS
- at `1024`, native RTDL is about `3.4x` faster than PostGIS
- at `2048`, native RTDL is about `3.3x` faster than PostGIS
- at `4096`, native RTDL is about `4.4x` faster than PostGIS
- at `8192`, native RTDL is about `4.8x` faster than PostGIS

## Boundary

- this is a bounded KITTI 3D `bounded_knn_rows` result on the current Linux
  host
- it does not claim generic 3D `knn_rows` closure
- it does not claim accelerated 3D backend closure
- it does not claim broader paper-family superiority beyond the measured
  duplicate-free KITTI bounded-KNN cases
