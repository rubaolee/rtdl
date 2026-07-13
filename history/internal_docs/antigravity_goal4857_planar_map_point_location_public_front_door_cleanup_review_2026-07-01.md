# Goal4857 Planar-Map Point-Location Public Front Door Cleanup Review

**Date:** 2026-07-01
**Reviewer:** Antigravity AI
**Status:** Approved
**Verdict:** `approve_goal4857_public_front_door_cleanup`
**Exit Label:** `completed_planar_map_point_location_public_front_door_cleanup`

---

## 1. Executive Summary

This review evaluates the cleanup of the Section 5.3 Point-in-Polygon (PIP) / planar-map point-location reproduction route under Goal4857. The target was to replace a legacy approach—which exposed internal environment variables (`RTDL_RAYJOIN_CDB_*`) and required custom wrapper scripts in user code—with a clean, unified public Python front door: `prepare_planar_map_point_location_2d_optix`.

Based on a thorough review of the codebase, internal evidence runners, regression tests, and public documentation, all claims are verified. The clean API boundary successfully encapsulates the environment bridge, ensures thread safety, preserves compatibility, and enforces correct documentation boundaries.

All tests passed successfully, and the changes are ready for release.

---

## 2. Answers to Review Questions

### Question 1: Does `prepare_planar_map_point_location_2d_optix` establish a cleaner public front door for Section 5.3-style planar-map point-location/PIP than the previous `prepare_directed_segment_point_location_2d_optix` plus user-side environment-variable wrapper?
**Yes.** The new function encapsulates the query execution wrapper pattern. Previously, user code had to manually set/reset environment variables or import the internal `_point_location_env` context manager and pair it with `prepare_directed_segment_point_location_2d_optix`.

With `prepare_planar_map_point_location_2d_optix`, the client code is clean, idiomatic, and simplified:
```python
with prepare_planar_map_point_location_2d_optix(base, query_map_id=1, scale_bounds=bounds) as pip:
    rows = pip.run_raw(points)
```

### Question 2: Is this cleanup generic at the API boundary, or does it hide a new RayJoin application-specific helper?
**It is generic.** The new classes `PreparedOptixPlanarMapPointLocation2D` and `prepare_planar_map_point_location_2d_optix` are generic primitives in `src/rtdsl/optix_runtime.py`. The primitive is formally declared as `PLANAR_MAP_POINT_LOCATION_2D` in the metadata. The implementation does not import or depend on `rtdsl.rayjoin_overlay`, and returning metadata states `bundled_rayjoin_helper_used: false` and `public_generic_rtdl_primitive: true`.

### Question 3: Is it acceptable that the lower native compatibility bridge still uses the historical `RTDL_RAYJOIN_CDB_*` environment variables internally, given that user/application code no longer sets them directly and the bridge is guarded and restored?
**Yes.** Modifying the compiled C++/CUDA native DLL interface (ABI parameters) represents a much larger, potentially breaking change. Guarding the environment variable updates via a process-local lock (`_PLANAR_MAP_POINT_LOCATION_ENV_LOCK = threading.RLock()`) and systematically restoring the original environment state using `try-finally` blocks prevents variable leakage and thread interference. This isolates the legacy design pattern entirely within the RTDL framework.

### Question 4: Do the new dataset aliases `chains_to_planar_map_segments` and `chains_to_planar_map_points` improve the public model without breaking legacy compatibility?
**Yes.** The new dataset adapter aliases in `src/rtdsl/datasets.py` provide clear, application-neutral terminology. They delegate directly to `chains_to_rayjoin_cdb_segments` and `chains_to_all_points`, keeping the face-id payloads intact for point-location/PIP/LSI while maintaining backward compatibility for legacy callers.

### Question 5: Do the Section 5.3 internal runners now use the new public front door and avoid direct `_point_location_env` / `RTDL_RAYJOIN_CDB_*` usage?
**Yes.** Both internal evidence runners (`history/internal_docs/goal4855_rayjoin_section53_pip_public_front_door.py` and `history/internal_docs/goal4856_rtdl_section53_pip_raw_diagnostic.py`) have been updated to import `prepare_planar_map_point_location_2d_optix`. They no longer define/import `_point_location_env` or directly manipulate `RTDL_RAYJOIN_CDB_*` variables.

### Question 6: Are the docs bounded correctly, avoiding Section 5.7 overlay, all-eight, broad RayJoin, or broad performance claims?
**Yes.** The updated documentation in `docs/rtdl_feature_guide.md`, `docs/features/engine_support_matrix.md`, `docs/features/pip/README.md`, and `docs/features/lsi/README.md` explicitly defines the scope of `planar_map_point_location_2d` and `planar_map_lsi_count_2d`. They explicitly note that these are count-only or point-location/PIP primitives and *do not* represent a polygon overlay, a full Section 5.7 overlay, or broad speedup/performance claims.

### Question 7: Are the tests sufficient for this cleanup level?
**Yes.** The test suite `tests/goal4857_planar_map_point_location_public_front_door_test.py` covers:
- Public export correctness in `rt.__all__`.
- The `native` support state in `engine_feature_support_matrix()`.
- Export of public dataset aliases.
- Correct isolation, lock thread safety, and restoration of the environment variables.
- Verification that the Section 5.3 runners do not import legacy wrappers.

### Question 8: Should Goal4857 close with `completed_planar_map_point_location_public_front_door_cleanup`?
**Yes.** The target criteria have been met. The exit label `completed_planar_map_point_location_public_front_door_cleanup` is fully justified.

---

## 3. Verification Details

### Automated Test Runs
The following test suites were successfully run in a PowerShell environment:
```powershell
$env:PYTHONPATH="src"
py -m unittest tests.goal4373_rayjoin_cdb_point_location_route_test tests.goal4857_planar_map_point_location_public_front_door_test tests.goal4851_planar_map_lsi_public_front_door_test
```

**Results:**
- **Tests run:** 11
- **Status:** OK (All passed in 0.035s)

---

## 4. Code & Architecture Review

### Environment Variable Encapsulation
In `src/rtdsl/optix_runtime.py`, environment changes are safely isolated:
```python
def _with_env(self, func):
    if self._closed:
        raise RuntimeError("prepared OptiX planar-map point-location handle is closed")
    with _PLANAR_MAP_POINT_LOCATION_ENV_LOCK:
        old = _set_planar_map_point_location_env(
            query_map_id=self.query_map_id,
            scale_bounds=self.scale_bounds,
        )
        try:
            return func()
        finally:
            _restore_planar_map_point_location_env(old)
```
- Thread safety is guaranteed via `_PLANAR_MAP_POINT_LOCATION_ENV_LOCK`.
- The `try-finally` block ensures that even if `func()` raises an exception, the environment is cleanly restored.

### Feature Matrix Mappings
In `src/rtdsl/engine_feature_matrix.py`, `planar_map_point_location_2d` is correctly configured:
- `optix`: `NATIVE`
- `embree`, `vulkan`, `hiprt`, `apple_rt`: `UNSUPPORTED_EXPLICIT` (with clear explanatory notes).

This aligns with the design rules where silent fallback is prohibited, and engines explicitly declare native capabilities.
