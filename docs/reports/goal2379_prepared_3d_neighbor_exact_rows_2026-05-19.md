# Goal2379 Prepared 3D Neighbor Exact Device Rows

Date: 2026-05-19

Status: implemented and pod-validated for the explicit exact-witness-row
contract.

## Purpose

Goal2377 added a fast distance-summary continuation. Some callers still need
actual witness rows: query id, neighbor id, and distance. Goal2379 adds an
explicit exact device row path for prepared 3D fixed-radius neighbors so those
callers can keep row output while avoiding the old host exact-refine loop.

This is not a ranked-K primitive and not an RTNN-specific engine hook. It is a
generic fixed-radius neighbor witness-row continuation.

## New Surface

- Native:
  - `rtdl_optix_run_prepared_exact_fixed_radius_neighbors_3d`
  - `fixed_radius_neighbors_3d_grid_exact_rows`
- Python:
  - `PreparedOptixFixedRadiusNeighbors3D.run_exact_raw(...)`
  - `PreparedOptixFixedRadiusNeighbors3D.run_exact(...)`
  - `scripts/goal2348_rtnn_v2_2_external_runner.py --result-mode exact-raw`

The existing prepared witness-row behavior remains available as `run_raw(...)`.
Goal2379 intentionally does not silently change that older contract.

## ABI Layout

The exact device row kernel writes the same POD layout downloaded by the native
host wrapper:

| Field | Type | Offset |
| --- | --- | ---: |
| `query_id` | `uint32_t` | 0 |
| `neighbor_id` | `uint32_t` | 4 |
| `distance` | `double` | 8 |

`RtdlFixedRadiusNeighborRow` is guarded with native `static_assert` checks for
the offsets above and a total size of 16 bytes.

## Pod Environment

- Pod SSH target: `root@69.30.85.177 -p 22055`
- Repository checkout: `/root/work/rtdl_goal2368`
- Base commit: `87e80048` plus Goal2379 patch
- GPU: NVIDIA RTX A5000
- Driver: `570.211.01`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`

## Results

| Count | Goal2371 old prepared rows warm sec | Goal2379 exact device rows warm sec | Old / exact ratio | Goal2371 rows | Goal2379 rows |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.007279 | 0.001928 | 3.78x | 206,434 | 205,874 |
| 262,144 | 0.090302 | 0.030799 | 2.93x | 2,512,822 | 2,517,940 |

Phase timings:

| Count | Upload sec | Exact count sec | Prefix/download sec | Exact row write sec | Row download sec | Host exact-refine sec |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.000247 | 0.000223 | 0.000131 | 0.000276 | 0.000601 | 0.0 |
| 262,144 | 0.001079 | 0.001552 | 0.000470 | 0.002431 | 0.021408 | 0.0 |

## Contract Boundary

This is an exact witness-row contract, not a summary contract and not a ranked
nearest-neighbor contract.

Put more plainly: it is not a ranked nearest-neighbor contract.

The row-count difference versus Goal2371 is expected. Goal2371 used a float
candidate stream plus host exact filtering. Goal2379 uses exact double-distance
counting and exact device row emission. It therefore matches Goal2377's exact
summary counts, not the older float-candidate witness counts.

This result does not authorize:

- RTNN paper-equivalence claims;
- RT-core speedup claims;
- broad nearest-neighbor acceleration claims;
- ranked-K semantics.

It is valid evidence that RTDL can expose a generic exact witness-row
continuation with no host exact-refine stage.

## Design Lesson

For v2.2 nearest-neighbor work, output contract choice matters as much as
traversal. The current ladder is now clearer:

- count summary: smallest output, fastest when only counts are needed;
- distance summary: aggregate distance statistics without row download;
- exact witness rows: IDs/distances with no host exact-refine;
- future ranked/grouped continuation: still needed when callers require
  nearest-K ordering or grouped app-level decisions.
