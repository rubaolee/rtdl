# Goal 217: OptiX `knn_rows`

## Goal

Close `knn_rows` on the OptiX backend for the reopened `v0.4` GPU-required
scope.

## Acceptance

- `rt.run_optix(...)` supports kernels lowered to `knn_rows`
- output rows preserve the public contract:
  - `query_id`
  - `neighbor_id`
  - `distance`
  - `neighbor_rank`
- rows remain grouped by ascending `query_id`
- within each query, rows remain ordered by ascending distance and then
  ascending `neighbor_id`
- Linux OptiX validation passes on the canonical GPU host

## Notes

- This goal uses the same bounded maturity pattern as
  `fixed_radius_neighbors` on OptiX:
  - CUDA-parallel brute-force per-query scan
  - float32 GPU distance computation
  - host-side row extraction and stable grouping
- Exact float parity is not required; row-level semantic parity is.
