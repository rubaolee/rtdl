# Goal585: Adaptive Backend Runtime Skeleton

Status: accepted, 3-AI implementation consensus reached

Date: 2026-04-18 local EDT

Consensus:

- Codex: ACCEPT, focused test passes and compatibility boundaries are visible.
- Claude: ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal585_claude_review_2026-04-18.md`.
- Gemini Flash: ACCEPT in
  `/Users/rl2025/rtdl_python_only/docs/reports/goal585_gemini_flash_review_2026-04-18.md`.

## Purpose

Goal585 starts the adaptive backend line approved in Goal584.  The goal is not
native performance yet.  It creates the public runtime contract, support matrix,
mode reporting, and prepared-execution placeholder required before native
branch/cache/layout kernels are added in later goals.

## Files Changed

- `/Users/rl2025/rtdl_python_only/src/rtdsl/adaptive_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal585_adaptive_backend_skeleton_test.py`

## Public Surface

New public names:

- `rt.run_adaptive(kernel, **inputs)`
- `rt.prepare_adaptive(kernel, **inputs)`
- `rt.adaptive_support_matrix()`
- `rt.adaptive_predicate_mode(kernel)`
- `rt.ADAPTIVE_BACKEND_NAME`
- `rt.ADAPTIVE_COMPAT_MODE`
- `rt.PreparedAdaptiveExecution`

## Current Execution Mode

Every Goal585 workload is deliberately marked:

- `mode`: `cpu_reference_compat`
- `native`: `False`
- `prepared_context`: `False`

`run_adaptive` validates that the compiled kernel belongs to the accepted
18-workload adaptive matrix, then executes through `run_cpu_python_reference`.

This is intentional.  It prevents fake acceleration claims while giving later
goals a stable backend API and compatibility baseline.

## 18-Workload Matrix

The skeleton support matrix contains:

1. `segment_intersection`
2. `point_in_polygon`
3. `overlay_compose`
4. `ray_triangle_hit_count_2d`
5. `ray_triangle_hit_count_3d`
6. `segment_polygon_hitcount`
7. `segment_polygon_anyhit_rows`
8. `point_nearest_segment`
9. `fixed_radius_neighbors_2d`
10. `fixed_radius_neighbors_3d`
11. `bounded_knn_rows_3d`
12. `knn_rows_2d`
13. `knn_rows_3d`
14. `bfs_discover`
15. `triangle_match`
16. `conjunctive_scan`
17. `grouped_count`
18. `grouped_sum`

## Design Decisions

- The adaptive backend is not a fixed-format BVH shim.
- The support matrix records per-family future layout, branch, and cache
  strategies.
- 2D/3D variants are classified from compiled input layouts.
- `bounded_knn_rows` is accepted only for the existing matrix-supported 3D
  variant.
- Prepared adaptive execution exists as a compatibility object now, but does
  not claim prepared native speedups.
- Goal585 scratch/allocation policy is conservative: inputs are read-only, and
  future native paths must use per-call or explicitly owned prepared-context
  scratch.

## Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal585_adaptive_backend_skeleton_test -v
```

Result:

```text
Ran 2 tests in 0.002s

OK
```

The focused test verifies:

- the support matrix has exactly 18 rows
- every row is compatibility mode and not native
- every workload routes through `run_adaptive`
- every workload matches `run_cpu_python_reference`
- every workload has visible mode metadata
- `prepare_adaptive(...).run()` matches the same reference output

## Known Boundary

This goal is a runtime skeleton, not a performance backend.  The first native
adaptive performance work remains Goal586, starting with ray/triangle kernels.

There is an unrelated local Apple RT experiment still dirty in the working tree.
It is not part of Goal585 and must not be included in the Goal585 commit.
