# Goal949 Graph Native Summary Continuation

Date: 2026-04-25

## Scope

Goal949 continues the app-native-continuation work after Goal948. It moves the
compact summary stage for the graph BFS and graph triangle-count examples from
Python summary loops into the native C++ oracle ABI.

This is intentionally bounded:

- It does not claim a full native BFS engine.
- It does not claim a full native triangle-analytics engine.
- It does not change the RT-core readiness boundary for graph apps.
- It does not add a new public speedup claim.

## Implementation

Added native ABI rows and functions:

- `RtdlBfsSummaryRow`
- `RtdlTriangleSummaryRow`
- `rtdl_oracle_summarize_bfs_rows`
- `rtdl_oracle_summarize_triangle_rows`

The Python runtime now exposes:

- `rt.summarize_bfs_rows(rows)`
- `rt.summarize_triangle_rows(rows)`

The public graph apps now use these helpers when `--output-mode summary` is
selected:

- `examples/rtdl_graph_bfs.py`
- `examples/rtdl_graph_triangle_count.py`
- `examples/rtdl_graph_analytics_app.py`

App payloads expose the continuation explicitly:

- `native_continuation_active`
- `native_continuation_backend: "oracle_cpp"`

## User-Facing Contract

Graph row modes still emit rows. Graph summary modes now emit compact summaries
through native C++ continuation:

- BFS summary: discovered edge count, discovered vertex count, max level.
- Triangle summary: triangle count, touched vertex count.

RTDL still owns the bounded graph candidate/refinement step. Python still owns
whole-workflow orchestration such as multi-level BFS control, shortest paths,
graph database behavior, distributed graph analytics, and app JSON assembly.

## Documentation Updated

Updated current public docs to reflect the native continuation:

- `docs/application_catalog.md`
- `docs/tutorials/graph_workloads.md`
- `examples/README.md`

Existing support-matrix wording already recorded the same boundary:

- `docs/app_engine_support_matrix.md`

## Verification

Focused graph gate:

```bash
RTDL_FORCE_ORACLE_REBUILD=1 PYTHONPATH=src:. python3 -m unittest \
  tests.goal949_graph_native_summary_continuation_test \
  tests.goal903_embree_graph_ray_traversal_test \
  tests.goal904_optix_graph_ray_mode_test \
  tests.goal889_graph_visibility_optix_gate_test -v
```

Result:

```text
Ran 18 tests in 0.185s
OK
```

Python syntax gate:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/oracle_runtime.py src/rtdsl/__init__.py \
  examples/rtdl_graph_bfs.py examples/rtdl_graph_triangle_count.py \
  examples/rtdl_graph_analytics_app.py \
  tests/goal949_graph_native_summary_continuation_test.py
```

Result: passed.

## Honesty Boundary

Allowed wording:

- graph summary mode uses native C++ continuation after emitted graph rows are
  produced.
- Embree graph BFS/triangle paths use CPU ray-tracing traversal for candidate
  generation where documented.
- OptiX graph claim scope remains bounded to reviewed RT traversal sub-paths
  and must stay tied to existing cloud evidence.

Disallowed wording:

- full native graph analytics engine.
- graph database acceleration.
- distributed graph analytics acceleration.
- shortest-path acceleration.
- new public speedup claim from this goal alone.
