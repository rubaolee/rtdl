# Goal 290 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 290 extended the duplicate-free KITTI three-way comparison to `8192`
points. The result does not introduce a new failure class. It confirms that the
large-set cuNSearch correctness boundary already captured at `4096` persists at
the next larger duplicate-free size.

## Duplicate-Free 8192 Result

Using the duplicate-free pair:

- query start index:
  - `0`
- search start index:
  - `3`
- query frame:
  - `0000000000`
- search frame:
  - `0000000003`
- duplicate match count:
  - `0`

The full three-way result at `8192` points was:

- RTDL reference median:
  - `14.159753 s`
- PostGIS 3D query median:
  - `0.799082 s`
- PostGIS prep:
  - `1.457378 s`
- cuNSearch CUDA execution median:
  - `0.117921 s`
- cuNSearch compile:
  - `3.080281 s`
- parity:
  - PostGIS: `true`
  - cuNSearch: `false`

## Honest Read

- PostGIS remains parity-clean on the bounded duplicate-free KITTI path
- cuNSearch remains faster than PostGIS in repeated execution time on this host
- cuNSearch remains correctness-blocked on the duplicate-free large-set path
- `8192` does not weaken the `4096` conclusion:
  - the current live cuNSearch comparison line is duplicate-free parity-clean
    through `2048`
  - and duplicate-free correctness-blocked at both `4096` and `8192`

This is a bounded host-specific continuation result, not a broad statement
about cuNSearch in general.
