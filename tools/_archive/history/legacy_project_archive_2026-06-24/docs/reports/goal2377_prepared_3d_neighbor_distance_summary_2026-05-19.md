# Goal2377 Prepared 3D Neighbor Distance Summary

Date: 2026-05-19

Status: implemented and pod-validated for the distance-summary contract.

## Purpose

Goal2375 proved that a count-only continuation can avoid the expensive witness
row stream for fixed-radius 3D neighbor search. Goal2377 extends that same
generic idea to distance summaries:

1. Reuse the prepared native 3D uniform-cell search structure.
2. Upload only query points for each run.
3. Launch a device kernel that performs exact double-distance filtering.
4. Return aggregate `count`, `min_distance`, `max_distance`, and
   `sum_distance`.
5. Avoid witness row allocation, row download, and host exact-refine.

This remains a generic primitive/continuation contract. It is not an RTNN
special case and does not add an app-shaped native ABI.

## New Surface

- Native:
  - `rtdl_optix_summarize_prepared_fixed_radius_neighbors_3d`
  - `fixed_radius_neighbors_3d_grid_exact_summary`
- Python:
  - `PreparedOptixFixedRadiusNeighbors3D.summary(...)`
  - `scripts/goal2348_rtnn_v2_2_external_runner.py --result-mode summary`

The native ABI also carries static layout checks for
`RtdlFixedRadiusNeighborSummary` so the host-side download struct remains a
64-bit, 32-byte POD matching the device summary layout.

## Contract Boundary

This is a distance-summary contract, not a witness-row contract. It is valid
when the caller needs aggregate distance statistics over bounded fixed-radius
neighbors. It is not a replacement for witness rows when the caller needs
neighbor IDs, per-neighbor distances, ranking, or downstream row-wise joins.

The path is app-agnostic and does not authorize:

- RTNN paper-equivalence claims;
- RT-core speedup claims;
- broad nearest-neighbor acceleration claims;
- replacement of witness-row semantics.

## Pod Environment

- Pod SSH target: `root@69.30.85.177 -p 22055`
- Repository checkout: `/root/work/rtdl_goal2368`
- Base commit: `b6d9a6ba` plus Goal2377 patch
- GPU: NVIDIA RTX A5000
- Driver: `570.211.01`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`
- Runner: `scripts/goal2377_native_prepared_frn3d_distance_summary_pod_runner.sh`

## Results

Goal2377 was measured against the same prepared 3D neighbor inputs used by
Goal2371 and Goal2375.

| Count | Goal2371 witness rows warm sec | Goal2375 count-summary warm sec | Goal2377 distance-summary warm sec | Witness-row / distance-summary ratio | Exact summary count | Sum distance |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.007279 | 0.006006 | 0.002548 | 2.86x | 205,874 | 2,098.645624 |
| 262,144 | 0.090302 | 0.003868 | 0.006451 | 14.00x | 2,517,940 | 33,785.778560 |

Phase timings:

| Count | Upload sec | Exact summary kernel sec | Summary download/reduce sec | Row download sec | Host exact-refine sec |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.000525 | 0.000359 | 0.001287 | 0.0 | 0.0 |
| 262,144 | 0.000747 | 0.002763 | 0.002507 | 0.0 | 0.0 |

The 262,144-point row confirms the intended shape: the continuation still pays
more arithmetic than count-only because it computes square roots and min/max/sum,
but it stays much faster than witness-row materialization because it downloads a
single aggregate summary instead of millions of rows.

## Design Lesson

RTDL v2.2 should keep separating traversal from output contracts. Serious
applications should be able to choose the smallest generic continuation that
matches their required output:

- witness rows for IDs and per-neighbor records;
- count summary for cardinality;
- distance summary for aggregate distance statistics;
- future ranked or grouped continuations for nearest/ranked outputs.
