# Goal2381 Prepared 3D Neighbor Ranked Rows

Date: 2026-05-19

Status: implemented and pod-validated for the bounded ranked-row contract.

## Purpose

Goal2379 made exact witness rows faster by removing host exact-refine. Those
rows are exact but not nearest-ranked. Goal2381 adds a bounded ranked
continuation over the same prepared 3D fixed-radius grid:

1. Reuse the prepared native 3D uniform-cell search structure.
2. Upload only query points.
3. Scan radius-neighbor candidates on device.
4. Keep the nearest `k_max` candidates per query in distance/id order.
5. Return `RtdlKnnNeighborRow` rows with `neighbor_rank`.

This is still a generic fixed-radius neighbor primitive. It is not an
RTNN-specific ABI, not a paper-equivalence claim, and not arbitrary ANN.

## New Surface

- Native:
  - `rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d`
  - `fixed_radius_neighbors_3d_grid_ranked_count`
  - `fixed_radius_neighbors_3d_grid_ranked_rows`
- Python:
  - `PreparedOptixFixedRadiusNeighbors3D.run_ranked_raw(...)`
  - `PreparedOptixFixedRadiusNeighbors3D.run_ranked(...)`
  - `scripts/goal2348_rtnn_v2_2_external_runner.py --result-mode ranked-raw`

The current implementation is intentionally bounded to `k_max <= 64`, because
each query maintains a local top-K buffer inside the device kernel.

## Pod Environment

- Pod SSH target: `root@69.30.85.177 -p 22055`
- Repository checkout: `/root/work/rtdl_goal2368`
- Base commit: `459bcc6c` plus Goal2381 patch
- GPU: NVIDIA RTX A5000
- Driver: `570.211.01`
- Build command: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`

## Correctness Probe

`ranked_correctness_small.json` compares the ranked native output against a
small Python oracle. The artifact reports `ok: true` and verifies rank order by
distance with id tie-breaking.

## Results

| Count | Goal2371 old prepared rows warm sec | Goal2379 exact unordered rows warm sec | Goal2381 ranked rows warm sec | Old / ranked ratio | Ranked / exact ratio | Rows |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.007279 | 0.001928 | 0.012287 | 0.59x | 6.37x | 205,874 |
| 262,144 | 0.090302 | 0.030799 | 0.047824 | 1.89x | 1.55x | 2,517,940 |

Phase timings:

| Count | Upload sec | Ranked count sec | Prefix/download sec | Ranked row write sec | Row download sec | Host exact-refine sec |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.003196 | 0.000266 | 0.000202 | 0.000313 | 0.000624 | 0.0 |
| 262,144 | 0.000743 | 0.005168 | 0.000493 | 0.005522 | 0.031049 | 0.0 |

## Contract Boundary

This is a bounded ranked fixed-radius contract. It is stronger semantically
than Goal2379 exact unordered rows, and therefore slower on this distribution.
That is expected: ranking must scan all radius candidates and maintain a local
top-K order, while the exact unordered row path can stop once it has emitted
`k_max` valid rows.

The 65,536-row case is not a speedup claim: the final clean rerun shows
small-input timing dominated by upload/setup variability. The 262,144-row case
is the useful scale point for this primitive and remains faster than the old
host-refined prepared witness-row path.

This result does not authorize:

- RTNN paper-equivalence claims;
- RT-core speedup claims;
- arbitrary ANN claims;
- broad nearest-neighbor acceleration claims.

It is valid evidence that RTDL can expose an app-agnostic ranked continuation
that beats the old host-refined prepared witness-row path at the larger measured
scale, while preserving a stricter nearest-ranked row contract.

## Design Lesson

The v2.2 nearest-neighbor ladder is now explicit:

- count summary: fastest when only cardinality is needed;
- distance summary: fastest when aggregate distance statistics are needed;
- exact unordered rows: fastest row-returning exact contract;
- ranked rows: stronger nearest-order semantics, with expected extra device
  work and larger row payload.

The next major performance work is not another app-specific trick. It is a
generic device-resident continuation/reduction framework so ranked/grouped
decisions can stay on device instead of returning millions of rows to the host.
