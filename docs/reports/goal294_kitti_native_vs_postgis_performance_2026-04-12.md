# Goal 294 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 294 measured the new native RTDL 3D fixed-radius path against the existing
Python truth path, PostGIS 3D, and cuNSearch on duplicate-free KITTI packages.

The most important result is:

- native RTDL now beats PostGIS on the measured KITTI 3D fixed-radius line
- native RTDL remains parity-clean against the Python truth path
- PostGIS remains parity-clean against the Python truth path
- cuNSearch remains correctness-blocked on the larger duplicate-free cases

## Results

### 512 points

- RTDL Python reference:
  - `0.056735 s`
- RTDL native oracle:
  - `0.001796 s`
- PostGIS 3D:
  - `0.010425 s`
- cuNSearch:
  - `0.109960 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`
  - cuNSearch: `true`

### 1024 points

- RTDL Python reference:
  - `0.222646 s`
- RTDL native oracle:
  - `0.003811 s`
- PostGIS 3D:
  - `0.017243 s`
- cuNSearch:
  - `0.106371 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`
  - cuNSearch: `true`

### 2048 points

- RTDL Python reference:
  - `0.886497 s`
- RTDL native oracle:
  - `0.010666 s`
- PostGIS 3D:
  - `0.048606 s`
- cuNSearch:
  - `0.099219 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`
  - cuNSearch: `true`

### 4096 points

- RTDL Python reference:
  - `3.562443 s`
- RTDL native oracle:
  - `0.035291 s`
- PostGIS 3D:
  - `0.208195 s`
- cuNSearch:
  - `0.124281 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`
  - cuNSearch: `false`

### 8192 points

- RTDL Python reference:
  - `14.253424 s`
- RTDL native oracle:
  - `0.131174 s`
- PostGIS 3D:
  - `0.809329 s`
- cuNSearch:
  - `0.126392 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`
  - cuNSearch: `false`

### 16384 points

- RTDL Python reference:
  - `56.436956 s`
- RTDL native oracle:
  - `0.437275 s`
- PostGIS 3D:
  - `1.970854 s`
- cuNSearch:
  - `0.130534 s`
- parity:
  - native RTDL: `true`
  - PostGIS: `true`
  - cuNSearch: `false`

## Honest Read

- the earlier “PostGIS beats RTDL” result was a Python-truth-path story
- after Goal 292 native closure, RTDL’s native fixed-radius path is now the
  relevant implementation path
- on the measured duplicate-free KITTI 3D fixed-radius line, native RTDL is
  faster than PostGIS from `512` through `16384`
- native RTDL also remains strictly parity-clean against the Python truth path
- cuNSearch remains competitive in raw execution time, but correctness-blocked
  on the larger duplicate-free cases

Useful bounded ratios:

- at `4096`, native RTDL is about `5.9x` faster than PostGIS
- at `8192`, native RTDL is about `6.2x` faster than PostGIS
- at `16384`, native RTDL is about `4.5x` faster than PostGIS

## Boundary

- this is a bounded KITTI 3D fixed-radius result on the current Linux host
- it is not yet a full claim about every RTDL workload family
- it does not yet cover the native 3D bounded-KNN path, which is still pending
  external-review closure in Goal 293
