# Goal 218: Vulkan `fixed_radius_neighbors`

## Goal

Make `fixed_radius_neighbors` runnable on Vulkan for the reopened `v0.4`
scope.

## Acceptance

- `rt.run_vulkan(...)` supports kernels lowered to `fixed_radius_neighbors`
- output rows preserve the public contract:
  - `query_id`
  - `neighbor_id`
  - `distance`
- rows remain grouped by ascending `query_id`
- within each query, rows remain ordered by ascending distance and then
  ascending `neighbor_id`
- per-query truncation to `k_max` remains correct
- Linux Vulkan validation passes on the canonical GPU host

## Notes

- This goal is correctness-first and runnability-first.
- Performance optimization is not part of the acceptance bar.
- The implementation intentionally mirrors the existing Vulkan brute-force
  compute structure used by the reopened nearest-neighbor line.
