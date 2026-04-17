# Goal 201 Fixed-Radius Neighbors External Baselines

## Goal

Add the first external baseline harness for `fixed_radius_neighbors`.

This goal closes the first non-RTDL comparison line for the new `v0.4`
workload without letting external systems define the workload contract.

## Scope

- add a SciPy `cKDTree` baseline for `fixed_radius_neighbors`
- add a bounded PostGIS helper for the same workload
- wire both through the baseline runner
- keep both baselines optional and honest
- preserve the RTDL contract exactly:
  - `distance <= radius`
  - per-query order by ascending `distance`, then ascending `neighbor_id`
  - global grouping by ascending `query_id`
  - truncation after ordering to `k_max`

## Non-goals

- no OptiX or Vulkan work
- no performance-win claim yet
- no requirement that SciPy or PostGIS be installed in the default first-run
  environment
- no change to the public workload contract

## Acceptance

This goal counts only if:

1. `fixed_radius_neighbors` can be compared against an external SciPy baseline
   through a checked-in helper
2. a bounded PostGIS helper exists for the same workload
3. baseline-runner support exists for the new external backends
4. authored and public-fixture tests cover the external baseline shape
5. docs state clearly that SciPy/PostGIS are optional comparison dependencies,
   not required for the normal RTDL first-run path
