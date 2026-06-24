# RTDL v0.4 Preview: Proposed Surfaces

## Headline public surface

- `fixed_radius_neighbors`

## Supporting surfaces

- `knn_rows`
- `nearest_distance`
- preserved `v0.3.0` visual-demo material as proof-of-capability history only

## Proposed first public user story

Users have:

- query points
- search points

They want:

- to find neighbors within a radius and emit row results

RTDL should provide:

- a bounded public workload for that task

## Proposed emitted fields

- `query_id`
- `neighbor_id`
- `distance`

## Proposed first boundary

- 2D points only
- Euclidean distance only
- explicit search radius semantics
- explicit `k_max` truncation semantics
- explicit backend support matrix
