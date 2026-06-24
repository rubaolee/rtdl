# Goal 219: Vulkan `knn_rows`

## Goal

Make `knn_rows` runnable on Vulkan for the reopened `v0.4` scope.

## Acceptance

- `rt.run_vulkan(...)` supports kernels lowered to `knn_rows`
- output rows preserve the public contract:
  - `query_id`
  - `neighbor_id`
  - `distance`
  - `neighbor_rank`
- rows remain grouped by ascending `query_id`
- within each query, rows remain ordered by ascending distance and then
  ascending `neighbor_id`
- Linux Vulkan validation passes on the canonical GPU host

## Notes

- This goal is correctness-first and runnability-first.
- Performance optimization is not part of the acceptance bar.
- The implementation intentionally mirrors the existing Vulkan
  `fixed_radius_neighbors` compute path:
  - one work item per query
  - brute-force scan over search points
  - fixed-size per-query output buffer
  - host-side filtering and stable grouping
