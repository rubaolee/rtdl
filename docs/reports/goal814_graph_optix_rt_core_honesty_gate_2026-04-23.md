# Goal 814: Graph OptiX RT-Core Honesty Gate

Date: 2026-04-23

Status: complete

## Problem

`examples/rtdl_graph_analytics_app.py` exposes `--backend optix`, but the
current OptiX graph implementation is a host-indexed CSR correctness path. The
native C++ symbols are explicitly implemented as host-indexed routines for BFS
expansion and triangle probing. That makes the path useful for parity and API
coverage, but not a NVIDIA RT-core traversal claim.

Without an explicit guard, cloud scripts or users could run:

```bash
python examples/rtdl_graph_analytics_app.py --backend optix
```

and incorrectly interpret the result as RT-core graph acceleration.

## Change

Added an explicit `--require-rt-core` honesty gate to:

- `examples/rtdl_graph_analytics_app.py`
- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`

When used with `--backend optix`, the flag fails before dispatching the backend:

```text
graph_analytics OptiX path is host-indexed fallback today, not NVIDIA RT-core traversal
```

When used with non-OptiX backends, the flag fails because it is specific to
NVIDIA RT-core claim-sensitive runs.

The normal `--backend optix` compatibility path remains available for existing
tests and correctness workflows.

## Current Graph Status

| Scenario | Current OptiX path | RT-core claim status |
| --- | --- | --- |
| BFS one-step expansion | host-indexed CSR expansion | no claim |
| Triangle count probe | host-indexed CSR set-intersection | no claim |
| Unified graph analytics app | wraps the two paths above | no claim |

## Required Future Work

To promote graph analytics, the next real implementation goal must replace the
host-indexed fallback with a traversal-native graph lowering. Acceptable future
directions include:

- encoding graph adjacency or edge intervals into OptiX custom primitives and
  using rays/probes for candidate discovery;
- compact native summary outputs for BFS frontier counts or triangle counts;
- phase-clean profiling that separates graph packing, acceleration-structure
  construction, traversal, output materialization, and Python summary work.

Until then, graph analytics remains `needs_rt_core_redesign` and
`needs_native_kernel_tuning`.

## Verification

Run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal814_graph_optix_rt_core_honesty_gate_test tests.goal705_optix_app_benchmark_readiness_test tests.goal803_rt_core_app_maturity_contract_test
python3 -m py_compile examples/rtdl_graph_analytics_app.py examples/rtdl_graph_bfs.py examples/rtdl_graph_triangle_count.py tests/goal814_graph_optix_rt_core_honesty_gate_test.py
git diff --check
```

Expected result: all tests pass and no whitespace errors.

## Release Boundary

This goal is an honesty and release-safety gate. It does not make graph
analytics RT-core accelerated and does not authorize any graph RTX performance
claim.
