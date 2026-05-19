# Goal2384 Prepared 3D Neighbor Ranked Summary Rows

Date: 2026-05-19

Status: implemented and pod-validated.

## Purpose

Goal2381 proved a generic ranked witness-row continuation, but it also showed
the next bottleneck: returning millions of rows to the host is expensive. For
many nearest-neighbor workloads a caller needs per-query ranked metadata, not
the full witness table.

Goal2384 adds a generic prepared 3D fixed-radius ranked-summary continuation.
For each query, the device keeps the nearest `k_max` candidates in distance/id
order and returns one summary row:

- `query_id`
- `neighbor_count`
- `nearest_neighbor_id`
- `kth_neighbor_id`
- `nearest_distance`
- `kth_distance`
- `sum_distance`

This is still app-agnostic RTDL runtime work. It is not RTNN-specific, not a
paper-equivalence claim, and not a user-defined shader mechanism.

## New Surface

- Native:
  - `rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d`
  - `fixed_radius_neighbors_3d_grid_ranked_summary`
  - `RtdlFixedRadiusRankedNeighborSummary`
- Python:
  - `PreparedOptixFixedRadiusNeighbors3D.run_ranked_summary_raw(...)`
  - `PreparedOptixFixedRadiusNeighbors3D.run_ranked_summary(...)`
  - `scripts/goal2348_rtnn_v2_2_external_runner.py --result-mode ranked-summary-raw`

The local top-K buffer is bounded to `k_max <= 64`, matching Goal2381.

## Pod Environment

- Pod SSH target: `root@69.30.85.177 -p 22055`
- Checkout: `/root/work/rtdl_goal2368`
- Base commit: `fd59109f` plus Goal2384 patch
- GPU: NVIDIA RTX A5000
- Driver: `570.211.01`
- Build: `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12`
- Runner: `STEP_TIMEOUT_SECONDS=900 REPEAT=5 bash scripts/goal2384_native_prepared_frn3d_ranked_summary_pod_runner.sh`
- Exit: `REMOTE_EXIT:0`

## Correctness

`ranked_summary_correctness_small.json` compares two query summaries against a
Python oracle and reports `ok: true`. The probe verifies nearest id, kth id,
nearest distance, kth distance, neighbor count, and top-K distance sum.

## Results

| Count | Goal2371 old prepared rows sec | Goal2381 ranked rows sec | Goal2384 ranked summary sec | Ranked rows / summary | Old rows / summary | Output rows |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.007279 | 0.012287 | 0.001526 | 8.05x | 4.77x | 65,536 |
| 262,144 | 0.090302 | 0.047824 | 0.008271 | 5.78x | 10.92x | 262,144 |

Phase timings:

| Count | Upload sec | Ranked summary kernel sec | Row download sec | Candidate rows summarized | Host exact-refine sec |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 0.000333 | 0.000350 | 0.000273 | 205,874 | 0.0 |
| 262,144 | 0.000849 | 0.005288 | 0.000860 | 2,517,940 | 0.0 |

## Interpretation

This is the first v2.2 nearest-neighbor result that cleanly demonstrates the
benefit of a device-resident continuation choice instead of row materialization.
The kernel still scans the same radius-neighbor candidate set as Goal2381, but
it writes one summary row per query rather than all ranked witness rows.

That is why the 262,144-row case improves from `0.047824s` ranked witness rows
to `0.008271s` ranked summary rows. The row download drops from millions of
witness records to one fixed-size record per query.

## Boundaries

This result authorizes a narrow claim:

RTDL can expose an app-agnostic prepared fixed-radius ranked-summary
continuation that preserves nearest/kth/sum metadata and avoids materializing
full witness rows.

This result does not authorize:

- RTNN paper-equivalence claims;
- RT-core nearest-neighbor claims;
- arbitrary ANN claims;
- broad nearest-neighbor acceleration claims;
- user-defined shader-extension claims.

## Design Lesson

The v2.2 nearest-neighbor ladder now has a sharper shape:

- count summary: cardinality only;
- distance summary: aggregate distance statistics only;
- exact unordered rows: full witness rows without ranking;
- ranked rows: full top-K witness rows;
- ranked summary rows: nearest/kth/sum metadata without full row materialization.

The remaining performance/design gap is a more general device-resident grouped
continuation framework for caller-selected reductions. Goal2384 is a concrete
generic step toward that direction, not the final abstraction.
