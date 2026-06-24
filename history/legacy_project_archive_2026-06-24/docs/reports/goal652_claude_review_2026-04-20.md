# Goal652 Claude Review: Apple RT 2D Native-Assisted Any-Hit

Date: 2026-04-20
Reviewer: Claude Sonnet 4.6

## Verdict: ACCEPT

No blockers found. The implementation is genuinely MPS-backed with per-ray early-exit, documentation is honest, and the stale-library fallback is intentionally documented.

---

## Scope Inspected

- `src/native/apple_rt/rtdl_apple_rt_mps_geometry.mm` lines 852–1109 (`rtdl_apple_rt_run_ray_anyhit_2d`)
- `src/rtdsl/apple_rt_runtime.py` lines 186–191, 620–644, 1324–1404, 1991–2186 (support-matrix entry, ctypes registration, dispatch function, `run_apple_rt` main path)
- `tests/goal652_apple_rt_2d_anyhit_native_test.py` (new test)
- `tests/goal603_apple_rt_native_contract_test.py` (updated contract assertions)
- `docs/backend_maturity.md`, `docs/capability_boundaries.md`, `docs/features/ray_tri_anyhit/README.md`, `docs/features/visibility_rows/README.md`, `docs/tutorials/feature_quickstart_cookbook.md` (doc changes for honesty boundary)

---

## Native Traversal: GENUINE

`rtdl_apple_rt_run_ray_anyhit_2d` is a real MPS-backed implementation:

**Prism encoding** (lines 981–1001): Each 2D triangle is extruded into 8 MPS triangles (2 caps + 6 lateral faces) spanning z ∈ [−1, +1]. Rays are encoded with `origin=(ox, oy, −1)`, `direction=(dx·tmax, dy·tmax, 2.0)`, `maxDistance=1.000001`. At t=1 the ray tip reaches z=+1, so the full 2D tmax extent maps onto a single prism traversal.

**Mask-based early-exit** (lines 963, 1075–1079): Per-chunk, each unresolved ray's mask is initialized to the chunk's full 32-bit primitive mask. When `ray_hits_triangle_2d()` confirms a 2D hit, `any_hits[ray_index]` is set and `gpu_rays[ray_index].mask` is zeroed — that ray is excluded from all subsequent MPS passes and chunks. The outer chunk loop is guarded by `unresolved_valid_rays > 0`.

**CPU exact-acceptance loop** (lines 1063–1086): After each MPS nearest-intersection pass, each candidate is checked via `ray_hits_triangle_2d()`. If rejected, only that triangle's bit is cleared from the ray's mask; the ray continues in subsequent passes. This is correct — MPS returns only one (nearest) intersection per pass, and masks steer it away from already-rejected candidates.

**MPSIntersectionTypeNearest** (line 1043): Correct intersection type for any-hit semantics. Hit-count traversal would use a different type; this confirms native-assisted traversal with early-exit intent.

**Memory management**: vertex_buffer and mask_buffer are manually retained/released at three consistent sites (error paths at lines 1009/1015 and 1037–1040, and normal exit at lines 1092–1094). No leak identified.

---

## Python Dispatch: CORRECT

ctypes argtypes for `rtdl_apple_rt_run_ray_anyhit_2d` (lines 634–644) match the C signature exactly: `(RtdlRay2D*, size_t, RtdlTriangle2D*, size_t, RtdlRayAnyHitRow**, size_t*, char*, size_t) → int`.

`ray_triangle_any_hit_apple_rt` (lines 1324–1404) correctly gates on type homogeneity: all-Ray2D + all-Triangle2D → 2D path; all-Ray3D + all-Triangle3D → 3D path; stale-library fallback (neither symbol present) → hit-count projection.

`run_apple_rt` dispatches at lines 2032–2035 before the `native_only` enforcement gate at line 2172. This is intentional: the hit-count projection path still uses the native Apple RT library (`rtdl_apple_rt_run_ray_hitcount_2d`), not the pure-Python CPU reference. The support matrix note at line 191 documents this explicitly.

---

## Tests: ADEQUATE

`goal652_apple_rt_2d_anyhit_native_test.py`:
- `test_native_2d_anyhit_symbol_matches_cpu_dispatch`: Tests a non-trivial 2-triangle, 3-ray case (ray 1 hits, ray 2 hits, ray 3 misses via tmax exclusion) against CPU reference — covers the hit/miss/tmax boundary contract.
- `test_native_2d_anyhit_handles_empty_build_side`: Tests the empty-triangle path that returns `any_hit=0` for all rays — mirrors the early-return at line 877.
- Skip guard correctly probes for the symbol via `_load_library()`.

`goal603_apple_rt_native_contract_test.py`:
- `test_current_native_rows_are_explicit` (lines 34–40) asserts `ray_triangle_any_hit` has `native_candidate_discovery="shape_dependent"`, correct `cpu_refinement`, and the expected notes strings — these are tight enough to catch regressions if the support matrix entry is edited carelessly.

---

## Documentation: HONEST

All updated docs consistently use the formulation "MPS prism traversal with per-ray mask early-exit plus exact 2D acceptance" and explicitly state "not programmable shader-level any-hit" in multiple locations:
- `capability_boundaries.md:130`
- `features/ray_tri_anyhit/README.md:66–67`
- `features/visibility_rows/README.md:57–58`
- `tutorials/feature_quickstart_cookbook.md:107`
- `backend_maturity.md:52–54`

No Apple 2D any-hit speedup claim is made anywhere in the updated docs. The stale-library fallback is documented in the support matrix notes. These meet the honesty boundary stated in the goal report.

---

## Notes (Non-Blocking)

**`native_only=True` with stale library**: When the 2D any-hit symbol is absent and `native_only=True` is passed, `ray_triangle_any_hit_apple_rt` silently falls back to hit-count projection via the native Apple RT library rather than raising `NotImplementedError`. This is intentional and documented in the support matrix notes. Callers who require confirmation of the direct any-hit symbol can check `hasattr(_load_library(), "rtdl_apple_rt_run_ray_anyhit_2d")` as shown in the test guard.

**chunk_size=32** is hardcoded (line 949). 32 is the MPS primitive mask bit-width limit, so this is a constraint, not an arbitrary tuning parameter. No issue.

**Inner pass loop variable `pass` is unused** as a value inside the loop body — the loop is purely for repetition. The compiler will warn about shadowing the keyword `pass` in some analysis tools, but in Objective-C++ this is fine.

---

## Summary

The 2D any-hit implementation uses real Metal/MPS RT hardware traversal (`MPSIntersectionTypeNearest` with prism geometry and per-ray mask early-exit), CPU exact 2D acceptance is correctly subordinate to MPS candidate discovery, the stale-library fallback is explicit and native-library-backed (not a silent drop to pure Python), and the docs make no overclaim about shader-level any-hit or unmeasured speedup. **ACCEPT.**
