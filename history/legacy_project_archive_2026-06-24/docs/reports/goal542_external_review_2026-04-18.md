# Goal 542 External Review: Prepared HIPRT Ray-Triangle Hit Count

Date: 2026-04-18
Reviewer: Claude (external review pass)

## Verdict: ACCEPT

## Separation of Preparation from Query Execution

Clean and correct. `PreparedRayHitcount3D` owns the runtime context, device vertex allocation, built `hiprtGeometry`, and compiled `oroFunction`. The prepare ABI (`rtdl_hiprt_prepare_ray_hitcount_3d`) performs all one-time costs: context init, triangle encode/upload, HIPRT geometry build, ORORTC kernel compile, and `hiprtBuildTraceKernelsFromBitcode`. The run ABI (`rtdl_hiprt_run_prepared_ray_hitcount_3d`) performs only per-query work: ray encode/upload, kernel launch, device-to-host copy. Performance smoke confirms the separation is effective — prepared queries run ~270x faster than one-shot.

## CPU-Oracle Parity

Both paths verified. The test suite covers:
- One-shot result equals `ray_triangle_hit_count_cpu` (ray ids 1–3, two triangles).
- `prepared.run(rays_a)` equals CPU oracle for rays_a.
- `prepared.run(rays_b)` equals CPU oracle for rays_b (same triangles, different batch).
- Performance report: `one_shot_parity: true`, `prepared_parity_all: true` across 5 repeats.

## Scope Honesty

Non-claims are explicit and appropriate: no AMD GPU, no HIPRT CPU fallback, no 2D support, no `run_hiprt` language-level dispatch, no large-scale perf suite. The smoke result is presented as a first positive signal, not a release-grade benchmark.

## Minor Observations (Non-Blocking)

1. **`triangleStride` inconsistency**: The one-shot path sets `mesh.triangleStride = sizeof(hiprtInt3)` (line 596) while `build_triangle_geometry` in the prepared path sets `triangleStride = 0` (line 385). Both use `triangleIndices = nullptr`, so the stride is irrelevant when indices are absent; parity tests pass in both cases. Harmless but worth aligning in a follow-up.

2. **No explicit `oroCtxSynchronize`**: Synchronization is implicit via the synchronous `oroMemcpyDtoH` call. Correct, but fragile if async copies are ever introduced.

3. **`__all__` export**: Both `prepare_hiprt_ray_triangle_hit_count` and `PreparedHiprtRayTriangleHitCount3D` are properly exported from `rtdsl.__init__`.

## Summary

The prepared HIPRT path correctly isolates build/compile cost from repeated query cost, preserves CPU-oracle parity across two independent ray batches, and makes no performance claims beyond what the Linux smoke test supports. The minor `triangleStride` inconsistency is not a correctness issue. **ACCEPT.**
