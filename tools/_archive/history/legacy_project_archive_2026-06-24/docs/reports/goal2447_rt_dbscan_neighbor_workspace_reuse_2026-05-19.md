# Goal2447 RT-DBSCAN Neighbor Workspace Reuse

Date: 2026-05-19

Status: implemented and pod-smoked.

## Purpose

Goal2444/2445 prepared the per-chunk adjacency offset columns once and reused
them across repeated RT-DBSCAN chunked continuation runs. The remaining small
chunk-overhead target is the `neighbor_indices` column that receives the OptiX
directed adjacency stream for each chunk.

Goal2447 adds an explicit opt-in path that allocates one bounded
`neighbor_indices` workspace sized to the largest planned chunk and reuses it
for every chunk.

## What Changed

`PreparedOptixCupyRadiusGraphChunkedAdjacency3D` now accepts:

```text
reuse_neighbor_index_workspace=False
```

The default remains the Goal2444 behavior: allocate one `neighbor_indices`
buffer per chunk to avoid cross-stream reuse hazards.

When `reuse_neighbor_index_workspace=True`, the prepared handle allocates:

```text
neighbor_index_workspace_size = max(chunk_directed_edge_counts)
neighbor_index_workspace = cupy.empty((neighbor_index_workspace_size,), int32)
```

and `_chunk_adjacency(...)` passes a slice of that workspace to the native
OptiX adjacency writer for the current chunk.

Metadata now reports:

- `neighbor_index_workspace_policy`
- `neighbor_index_workspace_reused`
- `neighbor_index_workspace_size`
- `chunk_sync_for_neighbor_index_workspace_reuse`

The research benchmark CLI exposes the option as:

```text
--reuse-chunk-neighbor-index-workspace
```

The repeat-probe script also accepts that option, plus
`--chunk-adjacency-edge-budget`, so pod runs can compare default per-chunk
allocation against synchronized single-workspace reuse on the same prepared
handle.

## Safety Boundary

This is an app-agnostic fixed-radius graph runtime improvement. It does not add
a DBSCAN-native ABI or any app-shaped native entry point.

The reuse path deliberately performs explicit chunk synchronization after each
CuPy union pass before the shared buffer can be overwritten by the next OptiX
write. This avoids the cross-stream reuse race that Goal2444 documented.

The tradeoff is measurable rather than assumed: a single prepared workspace can
reduce allocation pressure and peak temporary allocation churn, but the extra
chunk synchronization may reduce throughput. The option is therefore disabled
by default until pod evidence shows whether it is useful for performance,
memory control, or both.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2447_rt_dbscan_neighbor_workspace_reuse_test
```

The local test checks that:

- workspace reuse is explicit opt-in;
- the default policy still avoids the cross-stream race;
- metadata records the policy and workspace size;
- the reuse path synchronizes after each chunk union;
- the research benchmark exposes the option for pod measurement.

Pod smoke artifact:

```text
docs/reports/goal2447_rt_dbscan_neighbor_workspace_reuse_pod_smoke/summary.json
```

On the RTX A5000 pod, single-workspace reuse was correct but slower than the
default per-chunk allocation path on the 32,768-point clustered row:

- default steady-state mean: `0.41097885742783546` seconds
- single-workspace steady-state mean: `0.42906372901052237` seconds
- ratio: `1.0440043843030598x`

Conclusion: do not enable single-workspace reuse as a performance path.

## Verdict

`accept-with-boundary`.
