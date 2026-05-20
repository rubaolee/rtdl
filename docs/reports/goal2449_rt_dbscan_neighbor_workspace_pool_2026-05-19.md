# Goal2449 RT-DBSCAN Neighbor Workspace Pool

Date: 2026-05-19

Status: implemented and pod-smoked.

## Purpose

The first Goal2447 pod smoke showed that a single reused neighbor-index
workspace is correct but slower than default per-chunk allocation on the
32,768-point clustered row. The reason is simple: synchronizing after every
chunk costs more than the allocation churn it removes.

Goal2449 turns the idea into a bounded workspace pool. Instead of one reusable
buffer, the prepared handle can allocate `N` reusable buffers, each sized for
the largest planned chunk. The runtime synchronizes only before a pool slot
would be reused.

## What Changed

`PreparedOptixCupyRadiusGraphChunkedAdjacency3D` now accepts:

```text
neighbor_index_workspace_pool_size=0
```

Policy:

- `0`: default behavior, allocate `neighbor_indices` per chunk.
- `1`: single prepared workspace, equivalent to the Goal2447 opt-in path.
- `N > 1`: bounded workspace pool, reusing slot `chunk_index % N` and
  synchronizing only when `chunk_index >= N`.

The older boolean option remains as a shorthand:

```text
reuse_neighbor_index_workspace=True
```

which enables pool size `1` if no explicit pool size is given.

The research benchmark and repeat probe expose:

```text
--chunk-neighbor-index-workspace-pool-size N
```

## Boundary

This is still a generic fixed-radius graph/component runtime improvement. It
does not add DBSCAN-native ABI and does not put app logic into the engine.

This is not a speedup claim until pod evidence compares the pool against the
default per-chunk allocation path. The expected useful region is a middle pool
size, such as 4 or 8, where allocation churn is reduced without synchronizing
after every chunk or retaining a full unbounded adjacency stream.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2449_rt_dbscan_neighbor_workspace_pool_test
```

The test verifies that the pool is explicit, bounded, reported in metadata, and
available through the benchmark and repeat-probe CLIs.

Pod smoke artifact:

```text
docs/reports/goal2449_rt_dbscan_neighbor_workspace_pool_pod_smoke/summary.json
```

The RTX A5000 smoke compared default per-chunk allocation with pool sizes 4, 8,
and 18 on the 32,768-point clustered row:

| Policy | Steady-State Mean (s) | Ratio vs Default |
| --- | ---: | ---: |
| Default per-chunk allocation | 0.38809293260176975 | 1.000x |
| Pool size 4 | 0.4262925287087758 | 1.098x |
| Pool size 8 | 0.4073486079772313 | 1.050x |
| Pool size 18 | 0.3900656445572774 | 1.005x |

Conclusion: the bounded pool is correct, but it is not the next RT-DBSCAN
performance path. Synchronization and retained workspace pressure erase the
allocation benefit on this pod row. Keep the default allocation policy and move
the performance work to a lower-overhead generic grouped stream continuation.

## Verdict

`accept-with-boundary`.
