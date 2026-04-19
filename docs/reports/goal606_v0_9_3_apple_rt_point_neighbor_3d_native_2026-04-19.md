# Goal606: v0.9.3 Apple RT Native 3D Point-Neighborhood Workloads

Date: 2026-04-19

Status: accepted with 3-AI consensus

## Scope

Goal606 extends the Goal605 point-neighborhood native path from 2D to 3D:

- `fixed_radius_neighbors` for `Point3D/Point3D`
- `bounded_knn_rows` for `Point3D/Point3D`
- `knn_rows` for `Point3D/Point3D`

This completes Apple RT native candidate discovery for the current 2D and 3D
point-neighborhood family. It does not claim polygon, graph, or DB native
coverage.

## Implementation

Changed files:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_apple_rt.mm`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/apple_rt_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py`
- `/Users/rl2025/rtdl_python_only/tests/goal606_apple_rt_point_neighbor_3d_native_test.py`

Native lowering:

- Each 3D search point is represented as an MPS triangle cube with side length
  `2 * radius`.
- Each 3D query point casts a short z-ray through the cube volume.
- MPS masked traversal discovers candidate search points whose cubes contain
  the query point.
- CPU exact refinement computes Euclidean distance, filters by radius, sorts,
  truncates by `k_max`, and assigns neighbor ranks.

`knn_rows` uses a conservative combined-bounds radius, matching the existing RTDL
bounded-candidate approach for correctness. This is not a performance claim.

## Contract Update

`rt.apple_rt_support_matrix()` now reports:

| Predicate | Native candidate discovery | Native shapes |
| --- | --- | --- |
| `fixed_radius_neighbors` | `shape_dependent` | `Point2D/Point2D`, `Point3D/Point3D` |
| `bounded_knn_rows` | `shape_dependent` | `Point2D/Point2D`, `Point3D/Point3D` |
| `knn_rows` | `shape_dependent` | `Point2D/Point2D`, `Point3D/Point3D` |

The public direct helper `rt.fixed_radius_neighbors_3d_apple_rt` is exported for
direct parity tests.

`rt.apple_rt_predicate_mode()` now reports `native_mps_rt_2d_3d` for the
point-neighborhood predicate family, replacing the earlier 2D-only wording.

## Validation

Build:

```bash
make build-apple-rt
```

Focused test command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal578_apple_rt_backend_test tests.goal606_apple_rt_point_neighbor_3d_native_test tests.goal605_apple_rt_point_neighbor_2d_native_test tests.goal604_apple_rt_ray_hitcount_2d_native_test tests.goal603_apple_rt_native_contract_test tests.goal582_apple_rt_full_surface_dispatch_test -v
```

Actual result:

```text
Ran 25 tests in 0.061s
OK
```

Additional checks:

```bash
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/apple_rt_runtime.py src/rtdsl/__init__.py tests/goal606_apple_rt_point_neighbor_3d_native_test.py
git diff --check
```

Both completed with no output.

## Honesty Boundary

This is a correctness-first native coverage step. MPS performs conservative cube
candidate discovery, and CPU exact refinement handles distance, sorting, and
ranking. The path is hardware-backed but not yet optimized for throughput.

## Verdict

Codex verdict: ACCEPT with external consensus.

Goal606 correctly adds Apple MPS RT-backed 3D point-neighborhood candidate
discovery without extending claims to unrelated workload families.

External consensus:

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal606_external_review_2026-04-19.md` verdict ACCEPT; noted the stale mode string before it was corrected.
- Gemini review: `/Users/rl2025/rtdl_python_only/docs/reports/goal606_gemini_review_2026-04-19.md` verdict ACCEPT.
