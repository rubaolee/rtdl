# Goal596 External Review

Date: 2026-04-19

Reviewer: Claude Sonnet 4.6 (external review pass)

## Verdict: ACCEPT

## Findings

**Correctness — no issues found.**
- Native ABI (`rtdl_apple_rt_prepare_ray_closest_hit_3d`, `run_prepared_ray_closest_hit_3d`, `destroy_prepared_ray_closest_hit_3d`) is correctly implemented and error-path cleanup is thorough: all Metal objects released on failure inside `rtdl_apple_rt_prepare_ray_closest_hit_3d`, and the destructor (`~AppleRtClosestHitPrepared`) releases all retained objects in reverse-acquisition order.
- Python ctypes signatures match native signatures exactly. `_configure_library` wires all three new entry points with correct argtypes/restype.
- `PreparedAppleRtRayTriangleClosestHit3D` enforces use-after-close in both `run()` and `__enter__`, provides `__del__` as a safety net, and is idempotent on repeated `close()` calls.

**Public surface — clean.**
- `prepare_apple_rt_ray_triangle_closest_hit` and `PreparedAppleRtRayTriangleClosestHit3D` are exported in `__init__.py` with `__all__` entries. API matches the documented context-manager pattern.
- Dylib version bumped from 0.9.1 → 0.9.2 in both `rtdl_apple_rt_get_version` and the Python version check.

**Performance claim — appropriately bounded.**
- Report correctly labels both Apple RT paths as unstable (CV ≈ 0.65, above 0.15 threshold). Ratios are described as engineering-triage evidence only; no public speedup wording is asserted. This is the correct epistemic posture given the measurement noise.

**Test coverage — minimal but sufficient for scope.**
- `goal596_apple_rt_prepared_closest_hit_test.py` checks that prepared results match the one-shot path on a two-ray / one-triangle fixture. Covers the core correctness property. Use-after-close and empty-triangle-count edge cases are not tested, but these are implementation-internal guards, not public contracts.

**Minor observations (non-blocking).**
- `run_closest_hit_prepared` does not wrap its body in `@autoreleasepool`; the per-call `ray_buffer` and `intersection_buffer` Metal objects are released explicitly via `[... release]`, so there is no leak, but an autorelease pool would be the safer convention for future edits.
- The single test in `goal596_apple_rt_prepared_closest_hit_test.py` uses only one triangle; a two-triangle fixture would give slightly stronger confidence that `primitive_index → triangle_ids` mapping is correct, but the existing one-shot path uses the same mapping and is already covered by goal578 tests.

Both observations are cosmetic/defensive; neither warrants blocking.
