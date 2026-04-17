# Goal 200: Fixed-Radius Neighbors Embree Closure

## Objective

Close the first accelerated backend for `fixed_radius_neighbors` without
changing the accepted workload contract.

## Scope

In scope:

- add Embree execution support for `fixed_radius_neighbors`
- preserve the existing row contract:
  - `query_id`
  - `neighbor_id`
  - `distance`
- preserve the accepted semantics:
  - inclusive `distance <= radius`
  - ascending `query_id`
  - within-query ordering by ascending `distance`, then `neighbor_id`
  - `k_max` truncation after ordering
- add bounded authored and fixture parity tests against the Python truth path
- keep the closure correctness-first rather than performance-claim-first

Out of scope:

- OptiX or Vulkan
- broad performance claims
- `knn_rows`
- external benchmark publication

## Acceptance

Goal 200 is complete when:

1. `rt.run_embree(...)` supports `fixed_radius_neighbors`
2. authored-case parity passes against the Python truth path
3. fixture-case parity passes against the Python truth path
4. the out-of-order `query_id` ordering rule still holds
5. raw-mode field exposure is correct
6. the Embree library rebuild path notices edits in `src/native/embree/`
