# Goal2430 RT-DBSCAN Prepared Adjacency Stream Prototype

Date: 2026-05-19

Status: local wiring complete; pod steady-state evidence complete

## Purpose

Goal2428 scoped the remaining RT-DBSCAN weakness as a generic continuation
problem: counts and core flags alone cannot label connected components without
connectivity information.

Goal2430 adds the first partner-side prototype for that missing contract:

```text
prepared fixed-radius directed adjacency stream
  -> grouped union/find component continuation
```

This is deliberately partner-side CuPy work first. It lets RTDL test the stream
shape, metadata, app boundary, and correctness before adding any native OptiX
edge-stream writer.

## New Public Prototype

The new functions are:

```python
rt.prepare_radius_graph_adjacency_3d_cupy_partner_columns(...)
rt.radius_graph_components_3d_cupy_prepared_adjacency_partner_columns(...)
```

The RT-DBSCAN benchmark app exposes:

```text
partner_cupy_prepared_adjacency_components_3d
```

The prototype builds:

- `edge_offsets`: one offset per point plus a final end offset;
- `neighbor_indices`: a directed neighbor-index stream;
- exact `neighbor_counts`;
- component labels from a device-side union/find continuation over that stream.

## Pod Evidence

Environment:

```text
pod: root@69.30.85.177 -p 22055
commit: 660a35795cf906de211a177df95969068b22ca85
```

Artifacts:

```text
docs/reports/goal2430_rt_dbscan_prepared_adjacency_stream_pod/
```

Steady-state tail medians compare the prepared CuPy grid continuation against
the prepared adjacency continuation after both have already built their reusable
state:

| Dataset | Points | Prepared grid tail sec | Prepared adjacency tail sec | Adj / grid | Directed edges |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 4096 | 0.010134 | 0.001073 | 0.106x | 2114816 |
| `clustered3d` | 8192 | 0.021446 | 0.002416 | 0.113x | 8429946 |
| `clustered3d` | 16384 | 0.042476 | 0.005001 | 0.118x | 33880642 |
| `clustered3d` | 32768 | 0.108043 | 0.010556 | 0.098x | 136345976 |
| `road3d` | 4096 | 0.001772 | 0.000318 | 0.179x | 667400 |
| `road3d` | 32768 | 0.027747 | 0.002823 | 0.102x | 42790008 |
| `ngsim_dense` | 32768 | 0.011516 | 0.000408 | 0.035x | 6143054 |

Tiny and 4096-point rows matched the prepared-grid signatures. Larger rows were
timed without host row materialization to keep the probe focused on the device
continuation.

## Interpretation

The prototype clears an important uncertainty from Goal2428:

```text
If RTDL has a prepared adjacency stream, generic grouped union/find continuation
can avoid repeated distance checks and is much faster in steady state.
```

The tradeoff is also clear. The adjacency stream can become large: the 32768
clustered row materialized 136345976 directed edges. This is acceptable for the
measured pod smoke but not yet a universal plan. The next runtime step is a
bounded or chunked edge-stream contract, followed by a generic OptiX writer that
can produce the same stream without a CuPy distance pass.

## Boundary

This does not claim RT-core acceleration. It does not add native DBSCAN ABI.
It is a generic fixed-radius graph adjacency contract used by a DBSCAN-style
benchmark.

The next evidence step is not another DBSCAN shortcut. It is either:

- a bounded/chunked adjacency-stream continuation, or
- a generic prepared fixed-radius OptiX adjacency writer that feeds the same
  partner continuation.
