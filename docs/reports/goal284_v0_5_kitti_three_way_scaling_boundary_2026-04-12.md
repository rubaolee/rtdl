# Goal 284 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 284 extended the first bounded KITTI three-way benchmark into a small scaling sweep and found the current cuNSearch correctness boundary.

## Bounded Settings

- KITTI raw source:
  - `/home/lestat/data/kitti_raw`
- query frame:
  - start index `0`
- search frame:
  - start index `1`
- frames per package:
  - `1`
- radius:
  - `1.0`
- `k_max`:
  - `1`
- repeats:
  - `3`
- point counts:
  - `512`
  - `1024`

## Result

### 512 points

- RTDL reference median:
  - `0.056375 s`
- PostGIS 3D query median:
  - `0.010542 s`
- cuNSearch CUDA execution median:
  - `0.107593 s`
- parity:
  - PostGIS: `true`
  - cuNSearch: `true`

### 1024 points

- RTDL reference median:
  - `0.221360 s`
- PostGIS 3D query median:
  - `0.017584 s`
- cuNSearch CUDA execution median:
  - `0.099483 s`
- parity:
  - PostGIS: `true`
  - cuNSearch: `false`

## First cuNSearch Mismatch

At `1024` points, the first strict mismatch was:

- missing reference pair:
  - `(1008, 1007)`
- extra cuNSearch pair:
  - `(1008, 1008)`

First differing rows:

- RTDL reference:
  - `{"query_id": 1008, "neighbor_id": 1007, "distance": 0.0}`
- cuNSearch:
  - `{"query_id": 1008, "neighbor_id": 1008, "distance": 0.08324557843069172}`

Additional diagnostic probe:

- the `1024`-point package pair contains exactly one exact cross-package duplicate point
- that duplicate is:
  - query `1008`
  - search `1007`
- this is the same row where strict cuNSearch parity breaks

## Honest Read

- PostGIS remains both correct and fast across the `512 -> 1024` bounded sweep.
- cuNSearch remains fast enough to stay competitive on execution time, but strict row parity no longer holds at `1024`.
- the current evidence narrows that failure to a duplicate-point case, but does not yet prove the full root cause inside cuNSearch.
- the current live KITTI three-way line is therefore:
  - execution-complete for PostGIS through `1024`
  - execution-complete for cuNSearch through `1024`
  - correctness-closed for cuNSearch at `512`
  - correctness-blocked for cuNSearch at `1024`

This is not a broad paper-level conclusion. It is a bounded scaling result on the current host and current implementation line.
