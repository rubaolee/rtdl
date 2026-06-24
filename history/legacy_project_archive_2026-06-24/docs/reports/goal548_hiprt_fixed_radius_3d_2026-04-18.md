# Goal 548: HIPRT 3D Fixed-Radius Neighbor Traversal

Date: 2026-04-18

## Goal

Expand the v0.9 HIPRT backend beyond 3D ray/triangle hit counting by adding a real HIPRT traversal implementation for `fixed_radius_neighbors` over `Point3D` query and build inputs.

## Implementation Summary

- Added HIPRT custom AABB-list geometry for 3D search points.
- Added a HIPRT custom intersection function that tests exact point-to-query distance against the fixed radius.
- Added a HIPRT kernel that traverses the custom AABB geometry with `hiprtGeomCustomTraversalAnyHit`, collects the nearest in-radius neighbors up to `k_max`, and emits `query_id`, `neighbor_id`, and `distance`.
- Added the native C ABI function `rtdl_hiprt_run_fixed_radius_neighbors_3d`.
- Added Python `ctypes` dispatch through `fixed_radius_neighbors_3d_hiprt` and `rt.run_hiprt(...)`.
- Preserved explicit no-CPU-fallback behavior for unimplemented HIPRT peer workloads.

## Bounds

- Supported layout: `Point3DLayout` query points and `Point3DLayout` search points.
- Supported predicate: `rt.fixed_radius_neighbors(radius=..., k_max=...)`.
- Current `k_max` ceiling: `64`.
- Empty query or empty search input returns an empty result without attempting GPU traversal.
- 2D fixed-radius, KNN, graph, DB, and other peer workloads remain explicit `NotImplementedError` paths under the v0.9 goal ladder.

## Correctness Evidence

Local macOS Python-level validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal548_hiprt_fixed_radius_3d_test

Ran 11 tests in 0.003s
OK (skipped=2)
```

Linux HIPRT validation on `lestat-lx1`:

```text
make build-hiprt HIPRT_PREFIX=$HOME/vendor/hiprt-official/hiprtSdk-2.2.0e68f54
PYTHONPATH=src:. python3 -m unittest \
  tests.goal540_hiprt_probe_test \
  tests.goal541_hiprt_ray_hitcount_test \
  tests.goal543_hiprt_dispatch_test \
  tests.goal546_hiprt_api_parity_skeleton_test \
  tests.goal547_hiprt_correctness_matrix_test \
  tests.goal548_hiprt_fixed_radius_3d_test

Ran 20 tests in 5.842s
OK
```

Linux correctness matrix:

- Report: `/Users/rl2025/rtdl_python_only/docs/reports/goal548_hiprt_correctness_matrix_linux_2026-04-18.json`
- Summary: `pass=2`, `not_implemented=15`, `hiprt_unavailable=0`, `fail=0`
- Newly passing workload: `fixed_radius_neighbors_3d`

## Honesty Boundary

This is a real HIPRT traversal path, not a CPU fallback. The implementation uses HIPRT custom AABB geometry and custom any-hit traversal for row discovery. Current validation is on the Linux NVIDIA GTX 1070 HIPRT/Orochi CUDA path; this does not prove AMD GPU behavior and does not justify RT-core speedup claims on that machine.

## Status

Codex verdict: ACCEPT.

External AI review: Claude ACCEPT in `/Users/rl2025/rtdl_python_only/docs/reports/goal548_external_review_2026-04-18.md`.

Consensus: 2-AI ACCEPT. Goal 548 is closed.
