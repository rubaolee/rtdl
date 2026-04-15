# Goal 389 Report: v0.6 RT-Kernel BFS Python Truth Path

Date: 2026-04-14
Status: implemented

## Summary

This goal adds the first executable bounded RTDL graph-kernel slice:

- logical graph surface:
  - `rt.GraphCSR`
  - `rt.VertexFrontier`
  - `rt.VertexSet`
- graph RTDL predicate:
  - `rt.bfs_discover(...)`
- graph traverse mode:
  - `mode="graph_expand"`
- Python truth-path step execution for one BFS frontier expansion

The implemented surface allows users to write a bounded RTDL BFS expansion
kernel and execute it with `rt.run_cpu_python_reference(...)`.

The runtime also now rejects `rt.run_cpu(...)` for RT graph kernels with a
clear error, so the API boundary is honest while native/oracle graph execution
is still absent.

## Files Changed

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/layout_types.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/ir.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/api.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_reference.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal389_v0_6_rt_graph_bfs_truth_path_test.py`

## Implemented Behavior

The new Python truth-path behavior supports:

- CSR graph validation
- frontier items carrying:
  - `vertex_id`
  - `level`
- visited-set filtering
- same-step discovery dedupe
- deterministic output rows:
  - `src_vertex`
  - `dst_vertex`
  - `level`

The kernel form is:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_expand_reference():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])
```

## Verification

Focused new tests:

- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test`
  - `Ran 7 tests`
  - `OK`

Regression check:

- `python3 -m unittest tests.goal263_v0_5_bounded_knn_rows_surface_test`
  - `Ran 5 tests`
  - `OK`

Core quality:

- `python3 -m unittest tests.goal263_v0_5_bounded_knn_rows_surface_test tests.test_core_quality`
  - `Ran 110 tests`
  - `OK`

## Current Boundary

This is not yet:

- graph lowering
- native/oracle graph truth execution
- RT backend execution

It is the first honest executable RTDL-kernel BFS truth path in Python.
