# Goal 283 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 283 produced the first three-way KITTI performance result across RTDL reference, cuNSearch CUDA, and PostGIS 3D.

## Bounded Settings

- KITTI raw source:
  - `/home/lestat/data/kitti_raw`
- query frame:
  - start index `0`
- search frame:
  - start index `1`
- frames per package:
  - `1`
- points per package:
  - `512`
- radius:
  - `1.0`
- `k_max`:
  - `1`
- repeats:
  - `5`

## Method

- RTDL:
  - repeated Python truth-path execution on in-memory `Point3D` packages
- PostGIS:
  - one-time table load/index build measured separately
  - repeated 3D fixed-radius query execution measured separately
- cuNSearch:
  - one-time CUDA driver compilation measured separately
  - repeated binary execution measured separately

## Result

Median execution times:

- RTDL reference:
  - `0.056507 s`
- PostGIS 3D query:
  - `0.010436 s`
- cuNSearch CUDA execution:
  - `0.108413 s`

One-time setup costs:

- PostGIS prep:
  - `0.076574 s`
- cuNSearch compile:
  - `2.268842 s`

Parity:

- PostGIS parity vs RTDL:
  - `true`
- cuNSearch parity vs RTDL:
  - `true`

Row count:

- `391`

## Honest Read

On this bounded real KITTI case:

- PostGIS query execution is the fastest of the three measured execution paths
- RTDL Python truth path is slower than PostGIS query execution but faster than the current cuNSearch execution path
- cuNSearch execution is still meaningful, but its full path is dominated by compile cost unless the compiled driver is reused

This report does not claim broader paper-level superiority. It only closes the first honest three-way bounded KITTI result on the current host and current implementation line.
