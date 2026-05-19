# Goal2444 RT-DBSCAN Prepared Chunk Offsets

Date: 2026-05-19

Status: implemented locally, pending optional pod smoke.

## Purpose

Goal2441 made chunk ranges degree-budget-aware. The next lower-overhead step is
to avoid rebuilding each chunk's prefix offset column on every run.

Goal2444 prepares the per-chunk `edge_offsets` columns once after exact degree
counts are known, then reuses those offsets for every chunked adjacency run.

## What Changed

`PreparedOptixCupyRadiusGraphChunkedAdjacency3D` now stores:

- `chunk_edge_offsets`
- `chunk_directed_edge_counts`

The `_chunk_adjacency(...)` method now receives a `chunk_index` and reads:

```text
edge_offsets = self.chunk_edge_offsets[chunk_index]
directed_edge_count = self.chunk_directed_edge_counts[chunk_index]
```

so it no longer performs a per-run CuPy `cumsum` or allocates an offset column
for every chunk.

Metadata now reports:

- `prepared_chunk_edge_offsets_reused`
- `prepared_chunk_edge_offset_count`
- `prepared_chunk_edge_offsets_policy:
  degree_prefix_offsets_prepared_once_per_chunk`
- `neighbor_index_workspace_policy:
  allocated_per_chunk_to_avoid_cross_stream_reuse_race`

## Boundary

This is a generic fixed-radius chunked adjacency runtime improvement. It does
not add DBSCAN-native ABI and does not change native engine semantics.

The implementation deliberately does not reuse a single neighbor-index workspace
yet. Reusing one buffer across chunks could be faster, but it can also create a
cross-stream reuse race if OptiX writes and CuPy kernels are not ordered on the
same stream. That should be promoted only with a separate stream-semantics proof.

This is not a broad speedup claim, paper reproduction claim, or release claim.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2444_rt_dbscan_prepared_chunk_offsets_test
```

The focused test verifies that `_chunk_adjacency(...)` uses prepared offsets and
directed-edge counts rather than rebuilding offsets per run, and that the
cross-stream neighbor-index workspace boundary is documented.

## Verdict

`accept-with-boundary`.
