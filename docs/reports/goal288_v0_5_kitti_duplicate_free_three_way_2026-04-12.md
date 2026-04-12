# Goal 288 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 288 reran the KITTI three-way comparison on duplicate-free frame pairs and restored clean cuNSearch parity past the earlier duplicate-point boundary.

## Duplicate-Free Selections

For `1024` points:

- query start index:
  - `0`
- search start index:
  - `2`
- query frame id:
  - `0000000000`
- search frame id:
  - `0000000002`
- duplicate match count:
  - `0`

For `2048` points:

- query start index:
  - `0`
- search start index:
  - `3`
- query frame id:
  - `0000000000`
- search frame id:
  - `0000000003`
- duplicate match count:
  - `0`

## Result

### 1024 points, duplicate-free

- RTDL reference median:
  - `0.221285 s`
- PostGIS 3D query median:
  - `0.017256 s`
- cuNSearch CUDA execution median:
  - `0.111850 s`
- parity:
  - PostGIS: `true`
  - cuNSearch: `true`

### 2048 points, duplicate-free

- RTDL reference median:
  - `0.886594 s`
- PostGIS 3D query median:
  - `0.049127 s`
- cuNSearch CUDA execution median:
  - `0.098927 s`
- parity:
  - PostGIS: `true`
  - cuNSearch: `true`

## Honest Read

- the earlier `1024` cuNSearch failure was not a general scaling collapse
- once the selector removes duplicate-point packages, the current live cuNSearch line remains correct at both:
  - `1024`
  - `2048`
- PostGIS remains the fastest repeated execution path on these bounded cases
- cuNSearch remains slower than PostGIS on this host, but the correctness path is restored on duplicate-free packages

This is still a bounded result on the current host and implementation line, not a broad paper-level claim.
