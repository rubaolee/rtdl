# Goal 800 Graph OptiX Local Readiness Audit

Date: 2026-04-23

Status: local-first transparency guard complete

## Purpose

This goal audits whether the graph application family should enter the next
paid NVIDIA RTX cloud benchmark batch.

The answer is **no** for the current implementation.

## Files Checked

- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_analytics_app.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_bfs.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_triangle_count.py`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`
- `/Users/rl2025/rtdl_python_only/tests/goal692_optix_app_correctness_transparency_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal705_optix_app_benchmark_readiness_test.py`

## Finding

The OptiX graph API currently dispatches directly to host-indexed correctness
helpers:

- `run_bfs_expand_optix_host_indexed(...)`;
- `run_triangle_probe_optix_host_indexed(...)`.

There is no hidden native OptiX graph traversal mode comparable to the
experimental segment/polygon hit-count mode. The current graph paths are useful
as correctness and API-compatibility paths, but they are not NVIDIA RT-core
app-performance candidates.

## Changes Made

The graph app outputs now expose this boundary directly:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_analytics_app.py` now
  includes the app-level OptiX performance class and note from
  `rt.optix_app_performance_support("graph_analytics")`.
- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_bfs.py` now includes
  `optix_performance.class = host_indexed_fallback`.
- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_triangle_count.py` now
  includes `optix_performance.class = host_indexed_fallback`.

The transparency test now checks all three graph app surfaces.

## Verification

Focused tests:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal692_optix_app_correctness_transparency_test \
  tests.goal705_optix_app_benchmark_readiness_test
```

Result:

- `15` tests;
- `OK`.

Compile check:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile \
  examples/rtdl_graph_analytics_app.py \
  examples/rtdl_graph_bfs.py \
  examples/rtdl_graph_triangle_count.py \
  tests/goal692_optix_app_correctness_transparency_test.py
```

Result:

- `OK`.

## Release Boundary

Allowed statement:

- Graph apps are runnable through the OptiX backend interface for correctness,
  and their public JSON now explicitly states that the current OptiX graph path
  is host-indexed fallback.

Disallowed statements:

- RTDL graph apps are accelerated by NVIDIA RT cores today;
- BFS or triangle-count is an active RTX app benchmark candidate today;
- graph app performance should be measured on paid RTX cloud before a native
  graph traversal design exists.

## Next Step

Keep graph out of paid RTX cloud batches until there is a concrete RT lowering
for graph traversal, or explicitly reframe it as a non-RT CUDA/GPU graph
baseline. The immediate local-first work should move to the CUDA-through-OptiX
spatial apps (`hausdorff_distance`, `ann_candidate_search`, and
`barnes_hut_force_app`) and give them the same app-output transparency.
