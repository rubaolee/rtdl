# Goal2022 Graph Compressed Metric Pattern Perf

Date: 2026-05-14

Status: implementation slice with pod timing

## Purpose

After Goal2020 improved the polygon control rows, the remaining v2.0 weak spot
was graph analytics. The old Goal1972 row was fast, but it was still framed as a
small authored metric-table demo. The design problem was not raw speed alone:
we needed a reusable partner-side contract that explains why the graph row is
fast without adding graph semantics to the RTDL native engine.

Goal2022 adds that contract:

```text
partner_metric_table_reduce_repeated_pattern(...)
```

It reduces a generic metric/value pattern repeated `N` times without
materializing the repeated rows. For aligned metric patterns, the caller can set
`assume_aligned_output=True`, which means the pattern order already matches the
requested output metric order.

## What Changed

- Added a generic compressed metric-table reduction helper to
  `src/rtdsl/partner_adapters.py`.
- Exported it through `rtdsl.__init__`.
- Rewired the graph control app's CuPy path to use the compressed repeated
  metric pattern instead of materializing repeated metric rows.
- Preserved the CPU fallback and v1.8 oracle comparison path.

This does not add BFS, triangle counting, visibility, or graph traversal
semantics to the native engine. It is a generic repeated metric-table
continuation contract.

## Rejected Experiment

Before settling on the compressed pattern, I tested a device-constructed
`cp.tile(...)` metric payload. That avoided host arrays but was slower at this
scale because the graph pattern is tiny and the extra CuPy tiling kernels cost
more than the data they save. The useful lesson is that graph needs compressed
partner payloads, not merely device-side materialization of duplicate rows.

## Pod Evidence

Pod:

- Host: `69.30.85.251`
- SSH port: `22085`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- Checkout: `/root/rtdl_goal2000`
- Source label in artifacts: `local_goal2022_host_compressed_metric_pattern`
- Environment fix: installed `libgeos-dev` and `pkg-config` so the v1.8 native
  oracle could link against `libgeos_c`.

Artifacts:

- `docs/reports/goal2022_pod_graph_host_compressed_metric_pattern_1000.json`
- `docs/reports/goal2022_pod_graph_host_compressed_metric_pattern_100000_v2only.json`

| App | Copies | v1.8 median s | v2 median s | v2/v1.8 | Correct |
| --- | ---: | ---: | ---: | ---: | --- |
| `graph_analytics` | 1000 | 17.234474 | 0.000126 | 0.000007x | yes |
| `graph_analytics` | 100000 | skipped | 0.000124 | n/a | v2-only scale probe |

The 100,000-copy run intentionally skipped the v1.8 oracle timing because the
1,000-copy v1.8 median was already 17.2 seconds. The v2-only run confirms that
the compressed metric path does not scale with the repeated-row count for this
authored workload.

## Boundary

This is still a bounded graph-control result:

- It is a reusable compressed metric-table continuation, not broad graph
  traversal acceleration; in short, it is not broad graph traversal acceleration.
- It does not prove arbitrary BFS, triangle counting, or visibility algorithms
  are accelerated by RT cores.
- It does not authorize a whole-app graph speedup claim outside the measured
  authored contract.
- v2.0 release authorization still requires the final release audit and
  required external consensus.
