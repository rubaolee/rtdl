# Goal2958: RTNN Graph Replay Scale Chunking

Date: 2026-06-01
Status: pod scale stress passed

## Purpose

Goal2954 moved the canonical RTNN harness to the prepared-query CUDA graph
replay route. A larger 131,072-point stress run then exposed a user-facing
scalability guard: the OptiX graph replay implementation currently supports
`query_count <= 65536` per prepared graph. The old harness defaulted
`query_batch_size` to the full point count, so larger runs could fail unless
the user manually knew the hidden graph cap.

Goal2958 makes the harness choose a graph-safe default batch size:

```text
GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT = 65536
query_batch_size = min(point_count, GOAL2800_GRAPH_REPLAY_QUERY_BATCH_LIMIT)
```

This keeps the primitive generic and makes the Python entrypoint easier to use
at larger scale.

## Pod Evidence

Pod target: `root@69.30.85.171 -p 22167`

Source commit: `f880bf024f072e4e2dd143c845b2d10c30494f9a`

Artifact:

- `docs/reports/goal2958_rtnn_graph_replay_scale_pod/goal2958_rtnn_graph_131k.json`

131,072 query/search points, radius `0.02`, `k=50`, repeat `7`:

| Distribution | Query batches | RTDL sec | CuPy sec | CuPy/RTDL ratio |
| --- | ---: | ---: | ---: | ---: |
| uniform | `2` | `0.000325` | `0.000556` | `1.711x` |
| clustered | `2` | `0.062053` | `0.151121` | `2.435x` |
| shell | `2` | `0.002321` | `0.028535` | `12.296x` |

All rows matched the same-contract CuPy grid opponent:

- bounded neighbor count matches exactly;
- nearest and kth checksums match exactly;
- sum-distance differs only by expected float32 accumulation tolerance;
- native upload time remains `0.0`;
- no neighbor row materialization is introduced.

## Boundary

This goal fixes a graph-replay batching policy in the Python benchmark harness.
It does not add RTNN-specific native engine code and does not authorize public
speedup, broad RT-core, whole-app speedup, RTNN-paper reproduction, package
install, true zero-copy, Triton auto-selection, or v2.5 release claims.
