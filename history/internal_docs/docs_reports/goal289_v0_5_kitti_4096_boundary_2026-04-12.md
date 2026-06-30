# Goal 289 Report

Date: 2026-04-12
Workspace: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish`
Linux host: `lestat-lx1`

## Summary

Goal 289 captured the first large duplicate-free KITTI size where cuNSearch strict parity breaks again.

## Duplicate-Free 4096 Result

Using the duplicate-free pair:

- query start index:
  - `0`
- search start index:
  - `3`
- duplicate match count:
  - `0`

The full three-way result at `4096` points was:

- RTDL reference median:
  - `3.548221 s`
- PostGIS 3D query median:
  - `0.208282 s`
- cuNSearch CUDA execution median:
  - `0.122609 s`
- parity:
  - PostGIS: `true`
  - cuNSearch: `false`

## Mismatch Shape

For the full duplicate-free `4096` package:

- reference row count:
  - `2655`
- cuNSearch row count:
  - `2655`
- missing pair count:
  - `140`
- extra pair count:
  - `140`

First mismatch:

- reference:
  - `{"query_id": 291, "neighbor_id": 286, "distance": 0.34116129852451155}`
- cuNSearch:
  - `{"query_id": 291, "neighbor_id": 287, "distance": 0.3523232059214649}`

## Reduced-Candidate Probe

The first failing query (`291`) was rerun against its true top-20 RTDL candidates only.

Result:

- subset parity:
  - `true`
- cuNSearch returned the same ordered rows as the RTDL reference on that reduced set

## Honest Read

- this `4096` failure is not a duplicate-point issue
- it is also not explained by a simple local ordering or tie problem on the first failing query
- the first failing query becomes correct when the search set is reduced to its true top candidates
- that means the current live cuNSearch boundary is now:
  - duplicate-point-safe on duplicate-free packages through `2048`
  - large-set correctness-blocked at `4096`

This is a bounded host-specific result, not a broad statement about cuNSearch in general.
