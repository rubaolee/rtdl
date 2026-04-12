# Goal 291 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 291 extended the duplicate-free KITTI three-way comparison to `16384`
points. A duplicate-free pair still exists when the search window is widened to
include frame `0000000011`. The result does not introduce a new cuNSearch
failure class. It continues the existing large-set correctness boundary already
seen at `4096` and `8192`.

## Duplicate-Free 16384 Result

Using the duplicate-free pair:

- query start index:
  - `0`
- search start index:
  - `11`
- query frame:
  - `0000000000`
- search frame:
  - `0000000011`
- duplicate match count:
  - `0`

The full three-way result at `16384` points was:

- RTDL reference median:
  - `56.454320 s`
- PostGIS 3D query median:
  - `2.003480 s`
- PostGIS prep:
  - `2.638475 s`
- cuNSearch CUDA execution median:
  - `0.134252 s`
- cuNSearch compile:
  - `3.957363 s`
- parity:
  - PostGIS: `true`
  - cuNSearch: `false`

## Honest Read

- widening the search window changes duplicate-free package availability, not
  the correctness conclusion
- PostGIS remains parity-clean on the bounded duplicate-free KITTI path
- cuNSearch remains correctness-blocked on the duplicate-free large-set path
- the current honest line is now:
  - duplicate-free parity-clean through `2048`
  - duplicate-free correctness-blocked at `4096`, `8192`, and `16384`
- the RTDL Python reference path is still valid as truth, but by `16384` it has
  become materially expensive for repeated three-way scaling work on this host

This is a bounded host-specific continuation result, not a broad statement
about cuNSearch in general.
