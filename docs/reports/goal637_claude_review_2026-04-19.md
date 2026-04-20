# Goal 637 External Review — Claude Sonnet 4.6
Date: 2026-04-19

## Verdict: ACCEPT

---

## Findings

### C ABI (rtdl_optix_api.cpp / rtdl_optix_prelude.h)

- `RtdlRayAnyHitRow { uint32_t ray_id, any_hit; }` declared in prelude.h and consistent with `GpuRayAnyHitRecord { uint32_t ray_id, any_hit; }` in core.cpp. Layout-identical to `GpuRayHitRecord`, making the `reinterpret_cast` in the launch-params setup safe.
- Both `rtdl_optix_run_ray_anyhit` and `rtdl_optix_run_ray_anyhit_3d` are declared in the header and implemented in api.cpp with the standard null-check / zero-early-return pattern consistent with every other entry point.

### Kernel correctness (rtdl_optix_workloads.cpp)

- `ray_anyhit_kernel_source_2d()` (line 2075) performs a text substitution on the base hit-count kernel, replacing the any-hit body with `optixSetPayload_1(1u); optixTerminateRay();`. The substitution targets a unique, exact string; the `npos` guard at line 2090 raises a hard error if it fails — no silent wrong-behavior path.
- The raygen shader (inherited from `kRayHitCountKernelSrc`, line 1107) initialises `p1 = 0u` before calling `optixTrace`, so rays with no hit produce `any_hit = 0` correctly.
- `optixTerminateRay()` is the correct OptiX call for true early exit — it stops traversal immediately after the first accepted intersection, distinguishing this from the hit-count projection of Goal 636.
- The 3-D path (`ray_anyhit_kernel_source_3d`, line 2298–2318) applies the same substitution to `kRayHitCount3DKernelSrc` with its own `npos` guard.

### Python dispatch (optix_runtime.py)

- `run_optix` (dict mode): checks for native symbol via `_find_optional_backend_symbol`; routes to `_call_ray_anyhit_optix_packed` when present, falls back to hit-count projection for stale libraries. Fallback behavior is sound — `hit_count > 0` is semantically equivalent to `any_hit`.
- `prepare_optix` (raw mode): raises an informative error for stale libraries; does not silently fall back. Field names exposed are `("ray_id", "any_hit")` as required.
- `_call_ray_anyhit_optix_packed` (line 1424): dimension check before dispatching to 2-D vs 3-D symbol is correct. Both symbols are registered as optional, so a library built without them produces a clean error, not a segfault.

### Tests (goal637_optix_native_any_hit_test.py)

- 2-D test: three rays (hit, hit, miss), two triangles; verifies dict-mode parity with CPU and raw-mode field names + round-trip `to_dict_rows()`.
- 3-D test: two rays (hit, miss), one triangle; verifies dict-mode parity with CPU.
- Both are skipped cleanly on macOS (no OptiX hardware). Fixtures are minimal but sufficient to distinguish correct `any_hit=1`/`any_hit=0` from an accidental all-ones or all-zeros result.

### Performance claim

- Bounded micro-benchmark on a single dense-hit fixture on `lestat-lx1`. Clearly scoped, ratio reported (6.2×), and non-scope note explicitly disclaims sparse-hit cases and other backends. No issues.

### Non-scope confirmation

- No changes to Embree, HIPRT, Vulkan, or Apple RT runtimes. Other backends remain on the hit-count projection path from Goal 636, as intended.

---

## Issues

None.
