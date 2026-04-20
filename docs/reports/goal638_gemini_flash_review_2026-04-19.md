# Goal 638: v0.9.5 Embree Native Early-Exit Any-Hit - Gemini Flash Review

Date: 2026-04-19

## Review Verdict

**ACCEPT**

## Findings

The Goal638 implementation successfully introduces a genuine native `rtcOccluded1` early-exit any-hit path for Embree, as verified by:

1.  **C ABI and Native Implementation:** Confirmation of `RtdlRayAnyHitRow` structure, `rtdl_embree_run_ray_anyhit`, `rtdl_embree_run_ray_anyhit_3d` functions, and `triangle_occluded`/`triangle_occluded_3d` callbacks within the `native/embree/` directory. The usage of `rtcSetGeometryOccludedFunction` further validates the native occlusion traversal.
2.  **Python Integration:** `src/rtdsl/embree_runtime.py` correctly integrates the new native Embree C ABI functions. It intelligently attempts to use the native `rtdl_embree_run_ray_anyhit` and `rtdl_embree_run_ray_anyhit_3d` symbols, and includes a robust fallback mechanism to hit-count projection for backward compatibility with older libraries that may not export these new symbols.
3.  **Dedicated Testing:** `tests/goal638_embree_native_any_hit_test.py` specifically validates the correctness of both 2D and 3D Embree native any-hit functionality by comparing its output against the CPU reference implementation. It also confirms the structure of the raw row output.
4.  **Backend Dispatch and Compatibility Documentation:** `tests/goal636_backend_any_hit_dispatch_test.py` confirms that other backends (OptiX, Vulkan, HIPRT, Apple RT) continue to function correctly and align with their documented status as compatibility paths. Specifically, the test for Vulkan's `ray_triangle_any_hit` predicate correctly asserts that "raw mode is not supported", confirming that this backend relies on compatibility logic rather than a native raw any-hit implementation. This aligns with the "Non-Scope" section of the Goal638 report.

The changes are well-implemented, tested, and correctly documented regarding their scope and compatibility with other rendering technologies.
