# Goal 390 Report: v0.6 RT-Kernel Triangle Count Python Truth Path

Date: 2026-04-14
Status: implemented

## Summary

This goal adds the matching executable bounded RTDL graph-kernel slice for
triangle count:

- logical seed input:
  - `rt.EdgeSet`
- graph RTDL predicate:
  - `rt.triangle_match(...)`
- graph traverse mode:
  - `mode="graph_intersect"`
- Python truth-path step execution for one bounded triangle-probe step

The implemented surface allows users to write a bounded RTDL triangle-count
kernel and execute it with `rt.run_cpu_python_reference(...)`.

## Files Changed

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/graph_reference.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal390_v0_6_rt_graph_triangle_truth_path_test.py`

## Implemented Behavior

The new Python truth-path behavior supports:

- seed edges as:
  - `(u, v)` tuples
  - mappings with `u` and `v`
  - `rt.EdgeSeed`
- simple triangle discovery from a bounded seed batch
- uniqueness enforcement
- ascending ID ordering discipline
- deterministic triangle rows:
  - `u`
  - `v`
  - `w`

The kernel form is:

```python
@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_probe_reference():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(
        candidates,
        predicate=rt.triangle_match(order="id_ascending", unique=True),
    )
    return rt.emit(triangles, fields=["u", "v", "w"])
```

## Verification

Focused new tests:

- `python3 -m unittest tests.goal390_v0_6_rt_graph_triangle_truth_path_test`
  - `Ran 6 tests`
  - `OK`

Regression check:

- `python3 -m unittest tests.goal389_v0_6_rt_graph_bfs_truth_path_test tests.goal263_v0_5_bounded_knn_rows_surface_test tests.test_core_quality`
  - `Ran 117 tests`
  - `OK`

## Current Boundary

This is not yet:

- graph lowering
- native/oracle graph truth execution
- RT backend execution

It is the first honest executable RTDL-kernel triangle-count truth path in
Python.
