# Goal605: v0.9.3 Apple RT Native 2D Point-Neighborhood Workloads

Date: 2026-04-19

Status: accepted with 3-AI consensus

## Scope

Goal605 adds Apple Metal/MPS RT-backed candidate discovery for the 2D point
neighborhood workload family:

- `fixed_radius_neighbors` for `Point2D/Point2D`
- `bounded_knn_rows` for `Point2D/Point2D`
- `knn_rows` for `Point2D/Point2D`

3D point-neighborhood inputs remain CPU-reference compatibility paths for Apple
RT until a later v0.9.3 goal.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal603_apple_rt_native_contract_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal605_apple_rt_point_neighbor_2d_native_test.py`

Native lowering:

- Each 2D search point is represented as an MPS triangle-box prism whose XY
  bounds cover the query radius.
- Each 2D query point casts a short z-ray through those boxes.
- MPS masked traversal discovers candidate search points whose boxes contain
  the query XY coordinate.
- CPU exact refinement computes Euclidean distance and applies radius filtering,
  sort order, `k_max`, and neighbor rank.

`knn_rows` uses the same native candidate primitive with a conservative
dataset-level radius derived from the combined query/search bounds, then ranks
exactly on CPU. This is correctness-first and intentionally not a speedup claim.

## Contract Update

`rt.apple_rt_support_matrix()` now reports these rows as shape-dependent native:

| Predicate | Native candidate discovery | Native shapes |
| --- | --- | --- |
| `fixed_radius_neighbors` | `shape_dependent` | `Point2D/Point2D` |
| `bounded_knn_rows` | `shape_dependent` | `Point2D/Point2D` |
| `knn_rows` | `shape_dependent` | `Point2D/Point2D` |

`rt.apple_rt_predicate_mode()` reports
`native_mps_rt_2d_else_cpu_reference_compat` for these predicates. Unsupported
3D point cases still fall through to the existing `native_only=True` rejection.

## Validation

Build:

```bash
make build-apple-rt
```

Focused test command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Actual result:

```text
Ran 21 tests in 0.067s
OK
```

Additional checks:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal605_apple_rt_point_neighbor_2d_native_test.py
git diff --check
```

Both completed with no output.

## Honesty Boundary

This goal adds real Apple MPS candidate discovery for 2D point-neighborhood
workloads, but the path is not yet performance-optimized. The MPS geometry is a
conservative candidate filter; exact distance, sorting, and ranking remain CPU
refinement work. No throughput claim is made here.

## Verdict

Codex verdict: ACCEPT with external consensus.

Goal605 moves the 2D nearest-neighbor family from Apple RT compatibility-only
execution to native MPS-backed candidate discovery while preserving CPU oracle
parity for the public `run_apple_rt(..., native_only=True)` interface.

External consensus:

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal605_external_review_2026-04-19.md` verdict ACCEPT.
- Gemini review: `/Users/rl2025/rtdl_python_only/docs/reports/goal605_gemini_review_2026-04-19.md` verdict ACCEPT.
