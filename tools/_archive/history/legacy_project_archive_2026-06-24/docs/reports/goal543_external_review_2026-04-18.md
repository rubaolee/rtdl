# Goal 543 External Review: HIPRT Backend-Style Dispatch

**Date:** 2026-04-18
**Verdict:** ACCEPT

## Summary

`run_hiprt` and `prepare_hiprt` correctly expose backend-style dispatch for the 3D ray-triangle hit-count workload. The implementation is clean and well-bounded.

## Findings

**Dispatch correctness**
- `run_hiprt` validates the kernel shape, normalizes inputs, calls the existing `ray_triangle_hit_count_hiprt`, and projects output through `_project_rows` — same pipeline as other backends.
- `prepare_hiprt` correctly accepts only build inputs (triangles), delegates to `prepare_hiprt_ray_triangle_hit_count`, and wraps the result in `PreparedHiprtKernel`. Query rays are deferred to `prepared.run(rays=...)`.
- `PreparedHiprtKernel` is a proper context manager delegating `close()` to the underlying `PreparedHiprtRayTriangleHitCount3D`.

**CPU-reference parity**
- Linux smoke test: 1024 rays × 2048 triangles → 1952 hits, `run_hiprt_parity: true`, `prepare_hiprt_parity_all: true`.
- Unit tests assert `run_hiprt` and `prepared.run()` equal `run_cpu_python_reference` across two independent ray batches.

**Unsupported scope rejection**
- `_validate_hiprt_ray_hitcount_kernel` rejects 2D layouts, wrong geometry names, wrong roles, and non-`ray_triangle_hit_count` predicates before any library loading.
- `prepare_hiprt` rejects rays passed at prepare time with a clear message directing users to `prepared.run(rays=...)`.
- Both checked by local (no-hardware) unit tests.

**Public API**
- All new symbols (`run_hiprt`, `prepare_hiprt`, `PreparedHiprtKernel`, `PreparedHiprtRayTriangleHitCount3D`) are present in `__init__.py` imports and `__all__`.

## Concerns

None blocking. The dispatch surface is intentionally narrow (one workload, no fallback), and the non-claims are explicit.
