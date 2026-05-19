# Goal2433 RT-DBSCAN Chunked Adjacency Continuation

Date: 2026-05-19

Status: implemented and pod-smoked, with boundary.

## Purpose

Goal2431 proved that OptiX can write a generic directed fixed-radius adjacency
stream into caller-owned CuPy device columns. That cleared the architecture
problem but left an obvious memory problem: dense point sets can require one
giant `neighbor_indices` array.

Goal2433 adds a memory-bounded variant:

- count exact fixed-radius degrees for all points;
- process query points in chunks;
- ask OptiX to fill a bounded adjacency stream for each chunk;
- union core-core edges into one persistent CuPy parent workspace;
- refill chunks for final border/core labeling after union state is complete.

This keeps the primitive generic. It does not add DBSCAN-native engine code.

## New Public Runtime Surface

Python exports:

- `PreparedOptixCupyRadiusGraphChunkedAdjacency3D`
- `prepare_optix_cupy_radius_graph_chunked_adjacency_3d(...)`
- `radius_graph_components_3d_optix_cupy_prepared_chunked_adjacency_partner_columns(...)`

The RT-DBSCAN benchmark app adds:

- `optix_rt_core_chunked_adjacency_cupy_components_3d`

The repeat probe supports the same mode.

## Contract

The native engine still exposes only generic fixed-radius adjacency:

- no `dbscan` ABI;
- no DBSCAN-specific native control flow;
- no app-specific cluster expansion in C++.

The chunked adapter is Python+partner orchestration:

1. It prepares a generic OptiX 3-D fixed-radius scene.
2. It writes exact degree counts into CuPy columns by chunk.
3. It derives core flags in CuPy.
4. It fills bounded `edge_offsets` / `neighbor_indices` chunks through the
   Goal2431 OptiX writer.
5. It runs generic CuPy union/label kernels over chunks.

## Pod Evidence

Pod:

```text
ssh root@69.30.85.177 -p 22055 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Artifacts:

- `docs/reports/goal2433_rt_dbscan_chunked_adjacency_pod/tiny_app.json`
- `docs/reports/goal2433_rt_dbscan_chunked_adjacency_pod/clustered4096_repeat.json`
- `docs/reports/goal2433_rt_dbscan_chunked_adjacency_pod/clustered8192_repeat.json`
- `docs/reports/goal2433_rt_dbscan_chunked_adjacency_pod/clustered32768_chunked.json`

The exact tiny fixture passed:

- `matches_reference`: `true`
- `chunk_count`: `1`
- `total_directed_edge_count`: `33`

All repeat probes reported `signatures_match: true`.

## Performance And Memory Snapshot

The table uses tail median steady-state `outer_elapsed_sec` where repeats exist.
Lower is better.

| Dataset | Points | Mode | Total directed edges | Max chunk edges | Chunks | Tail/runtime (s) |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `clustered3d` | 4096 | full OptiX adjacency | 2,114,816 | n/a | n/a | 0.007117 |
| `clustered3d` | 4096 | chunked OptiX adjacency | 2,114,816 | 2,114,816 | 1 | 0.022417 |
| `clustered3d` | 8192 | full OptiX adjacency | 8,429,946 | n/a | n/a | 0.016442 |
| `clustered3d` | 8192 | chunked OptiX adjacency | 8,429,946 | 4,222,317 | 2 | 0.053785 |
| `clustered3d` | 32768 | chunked OptiX adjacency | 136,345,984 | 17,197,789 | 8 | 0.746450 |

Interpretation:

- Chunked adjacency is correct.
- It reduces peak adjacency storage pressure from one full stream to a bounded
  per-chunk stream.
- It is slower than full adjacency when full adjacency fits in memory, because
  it currently writes adjacency twice: once for union and once for labels.
- It is still useful as a generic memory contract for dense rows that cannot or
  should not allocate one giant neighbor table.

## Design Conclusion

This solves the immediate memory-contract problem, not the performance problem.
The next performance-oriented design should reduce the second adjacency pass or
avoid materialized neighbor indices altogether through a grouped/chunked
continuation primitive.

Promising follow-up directions:

1. Write border-label candidates during the union pass into a bounded temporary
   stream, avoiding a second RT adjacency fill.
2. Add a generic chunked grouped-reduction continuation so callers can express
   union/count/parity/max over streams without owning a full edge table.
3. Let the planner choose among prepared grid, full adjacency, and chunked
   adjacency explicitly with recorded plan metadata; do not hide this behind
   magic dispatch.

## Verdict

`accept-with-boundary`.

Goal2433 is a correct generic memory-bounded continuation path. It is not a
speedup claim and should not replace the faster full-stream path when memory is
available.
