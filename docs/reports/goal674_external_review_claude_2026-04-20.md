# Goal 674 External Review — HIPRT Prepared 2D Any-Hit

Reviewer: Claude Sonnet 4.6
Date: 2026-04-20

## Verdict: ACCEPT

The implementation is correct, well-bounded, and consistent with the project's existing prepared-handle pattern.

---

## Native layer (rtdl_hiprt_core.cpp / rtdl_hiprt_api.cpp)

**Struct design.** `PreparedRayAnyhit2D` mirrors `PreparedRayHitcount3D` structurally. It owns the runtime, both device allocations (triangle and AABB), the HIPRT geometry, the function table, and the JIT-compiled kernel. All five resources are released in the destructor in the right order (func_table → geometry), which matches how HIPRT requires cleanup.

**Empty-scene fast-path.** The `empty_scene` bool is set on the trivial constructor and checked early in `run_prepared_ray_anyhit_2d`. Zero-ray and empty-scene returns are properly handled without launching a kernel, consistent with the direct path.

**Kernel source generation.** `ray_anyhit_kernel_source_2d` derives the any-hit kernel from the existing hit-count 2D source via four targeted string substitutions. The critical one — replacing `++any_hit;` with `any_hit = 1u;\n            break;` — is the correct early-exit transform for any-hit semantics. This is the same derivation strategy used for the 3D any-hit kernel, which is already validated.

**AABB padding.** `encode_triangle_2d_aabbs` applies a `1e-4f` epsilon pad consistently on all six faces (including the degenerate z-axis), identical to what the direct unprepared 2D any-hit path uses. No regression here.

**uint32_t overflow guards.** Both prepare and run check `triangle_count > UINT32_MAX` and `ray_count > UINT32_MAX` and throw with a clear message before any cast. This matches the existing guards in other prepared paths.

**Exception safety in prepare.** The try/catch in `rtdl_hiprt_prepare_ray_anyhit_2d` correctly nullifies and destroys both `func_table` and `geometry` on failure before rethrowing. The geometry null-check before destroy is correct because `geometry = nullptr` is set after the successful `*prepared_out = new ...` assignment, which transfers ownership.

**run_prepared_ray_anyhit_2d null-check gap.** The `run_prepared_ray_anyhit_2d` API wrapper in `rtdl_hiprt_api.cpp` does not guard against `ray_count == 0 && rays == nullptr` before delegating — but the core function handles it immediately via the `ray_count == 0` early return, so no null dereference occurs. Not a bug, but it differs slightly from the zero-count guard pattern in the direct `run_ray_anyhit_2d` wrapper.

---

## Python layer (hiprt_runtime.py / __init__.py)

**`PreparedHiprtRayTriangleAnyHit2D`** follows the same context-manager / `close()` / `_closed` guard pattern as every other prepared handle. The `close()` method skips the native destroy call for the empty-scene case (where `handle` is a null `c_void_p`), which is correct.

**`prepare_hiprt_ray_triangle_any_hit_2d`** correctly validates that all inputs are `_CanonicalTriangle2D`, encodes the triangle array, and delegates to `rtdl_hiprt_prepare_ray_anyhit_2d`. The symbol-availability check (`_hiprt_prepared_ray_anyhit_2d_symbols_available`) allows the empty-scene path to work without a native build, consistent with the portability design used elsewhere.

**`prepare_hiprt` dispatcher.** The updated dispatcher explicitly rejects Ray2D/Triangle2D any-hit for anything other than the 2D layout pair, and explicitly rejects prepared 3D any-hit with a clear "Ray2D/Triangle2D any-hit" error message. The test `test_prepared_3d_anyhit_is_explicitly_not_claimed` validates this fence.

**`__init__.py` exports.** Both `PreparedHiprtRayTriangleAnyHit2D` and `prepare_hiprt_ray_triangle_any_hit_2d` are exported in `__all__`. No missing public surface.

---

## Test coverage

| Case | Test |
|---|---|
| Direct prepared 2D any-hit matches CPU oracle | `test_prepared_2d_anyhit_matches_cpu_and_direct_hiprt` |
| Generic `rt.prepare_hiprt(...)` prepared 2D any-hit matches CPU | same test |
| Prepared handle reused across multiple ray batches | `test_prepared_2d_anyhit_reuses_scene_for_multiple_ray_batches` |
| Empty prepared scene (portable, no native lib) | `test_empty_prepared_scene_runs_without_native_symbols` |
| 3D ray input rejected by closed-typed prepared handle | `test_prepared_anyhit_rejects_3d_rays_portably` |
| Closed handle rejected | `test_closed_empty_prepared_scene_is_rejected` |
| Prepared 3D any-hit explicitly rejected | `test_prepared_3d_anyhit_is_explicitly_not_claimed` |

Coverage is complete for the claimed scope. Regression suites (`goal639`, `goal543`) were run alongside and passed.

---

## Performance claim assessment

The reported 77× speedup (direct median 580 ms → prepared query median 7.5 ms, 4096 rays / 1024 triangles, all-hit) is a reasonable repeated-query result. The prepared path eliminates: Orochi context creation, HIPRT context creation, two host-to-device uploads (triangles and AABBs), AABB geometry build, function table creation, and JIT kernel compilation. These are all one-time costs per prepare call, so the magnitude is plausible for this workload size. The samples (3 direct, 6 prepared) are sufficient for a sanity measurement at this scale. The report correctly does not claim scalar-count-only or prepacked-ray savings.

The claim is honestly bounded:
- Measured on NVIDIA hardware via HIPRT's CUDA/Orochi path; AMD GPU not validated.
- Not a count-only optimization.
- No prepacked ray buffer.
- No prepared 3D any-hit.

---

## Issues

None blocking acceptance.

One minor note: the kernel source derivation in `ray_anyhit_kernel_source_2d` is fragile against future refactors of `ray_hitcount_2d_kernel_source` that rename internal variables. This is the same accepted tradeoff as the 3D any-hit path and is understood project-wide.

---

## Summary

Goal 674 adds a complete, exception-safe, portably-testable prepared 2D any-hit path for HIPRT. The implementation is structurally consistent with existing prepared handles, the performance claim is honestly bounded, and the test suite covers all stated correctness conditions. No regressions identified.

**External review verdict: ACCEPT.**
