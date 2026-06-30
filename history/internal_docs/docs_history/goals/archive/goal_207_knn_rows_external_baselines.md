# Goal 207: KNN Rows External Baselines

## Goal

Add the first external baseline harness for `knn_rows`.

This closes the first non-RTDL comparison line for the second `v0.4`
nearest-neighbor workload without letting external systems define the contract.

## Scope

- add a SciPy `cKDTree` baseline for `knn_rows`
- add a bounded PostGIS helper for the same workload
- wire both through the baseline runner
- keep both baselines optional and honest
- preserve the RTDL contract exactly:
  - per-query order by ascending `distance`, then ascending `neighbor_id`
  - global grouping by ascending `query_id`
  - explicit 1-based `neighbor_rank`
  - emit all available rows when fewer than `k` candidates exist

## Non-goals

- no GPU/backend work
- no performance-win claim yet
- no requirement that SciPy or PostGIS be installed in the default first-run environment
- no change to the public workload contract

## Acceptance

1. `knn_rows` can be compared against an external SciPy baseline through a checked-in helper
2. a bounded PostGIS helper exists for the same workload
3. baseline-runner support exists for the new external backends
4. authored and public-fixture tests cover the external baseline shape
5. docs state clearly that SciPy/PostGIS are optional comparison dependencies, not required for the normal RTDL first-run path
