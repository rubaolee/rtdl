# Goal582: Gemini Flash Review - Apple RT Full-Surface Compatibility Dispatch

Verdict: **ACCEPT**

## Reasons

1. **Correct Dispatch Logic**: `run_apple_rt` correctly distinguishes between the native Apple Metal/MPS path (currently 3D `ray_triangle_closest_hit`) and the CPU Python reference compatibility path for all other 17 predicates.
2. **Honest Implementation**: Non-native paths are explicitly routed through `_run_cpu_python_reference_from_normalized` after ensuring the Apple RT library is loaded, maintaining the "backend must be available" contract even for compatibility dispatch.
3. **Robust Rejection**: The `native_only=True` parameter successfully blocks compatibility paths with an informative `NotImplementedError`, preventing silent fallback to CPU when hardware acceleration is requested.
4. **Verified Coverage**: All 18 current RTDL predicates are covered by tests in `tests/goal582_apple_rt_full_surface_dispatch_test.py` and verified against the CPU reference baseline.
5. **Transparent Documentation**: README and capability boundary docs clearly state that "full-surface support" is achieved through compatibility dispatch, distinguishing it from full native parity or speedup claims.

## Observation

`apple_rt_predicate_mode` and `apple_rt_support_matrix` are correctly imported in `src/rtdsl/__init__.py` and are accessible as `rt.apple_rt_support_matrix()`, but they are currently omitted from the `__all__` list in that file. This does not affect technical correctness or documented usage, but should be updated in a subsequent maintenance task.
