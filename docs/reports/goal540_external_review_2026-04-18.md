# Goal 540 External Review: HIPRT Probe Backend Bring-Up

Date: 2026-04-18  
Reviewer: Claude Sonnet 4.6 (external review pass)

## Verdict: ACCEPT

---

## What Was Reviewed

- `src/native/rtdl_hiprt.cpp` — native shim
- `src/rtdsl/hiprt_runtime.py` — Python ctypes loader
- `src/rtdsl/__init__.py` — public export surface
- `tests/goal540_hiprt_probe_test.py` — skip-safe test suite
- `Makefile` — `build-hiprt` target
- `docs/reports/goal540_hiprt_probe_backend_bringup_2026-04-18.md` — execution report

---

## Correctness Assessment

**Native shim (`rtdl_hiprt.cpp`):** Two exported functions, both correct. `rtdl_hiprt_get_version` returns compile-time HIPRT version macros. `rtdl_hiprt_context_probe` sequences Orochi CUDA init → device get → context create → device properties → HIPRT context create/destroy, with proper error propagation and cleanup on every failure path. Device type detection via `strstr(props.name, "NVIDIA")` is appropriate for the CUDA-path-only scope. Cleanup ordering (hiprt destroy before oro destroy, with error check after) is correct.

**Python loader (`hiprt_runtime.py`):** `lru_cache` on library loading avoids repeated dlopen. Library resolution order (env var → build dir → system) is sensible. `argtypes`/`restype` declarations match the C signatures exactly. `FileNotFoundError` on missing library degrades cleanly. No import-time library loading — the library is deferred to first function call.

**Export surface (`__init__.py`):** `hiprt_version` and `hiprt_context_probe` are present in both the module-level imports and `__all__`. No other exports modified. No regression risk to existing backends.

**Makefile:** `build-hiprt` includes the required Orochi translation units (`Orochi.cpp`, `OrochiUtils.cpp`, `cuew.cpp`, `hipew.cpp`), correct `-DOROCHI_ENABLE_CUEW` define, and embeds RPATH via `-Wl,-rpath`. Header guard check provides a clear error message on missing SDK. Candidate path list covers the documented SDK layout.

**Tests:** Skip guard via `_hiprt_available()` works correctly — macOS skips cleanly, Linux passes on real hardware. Test assertions (major ≥ 2, api_version ≥ 2000, device_type in {0,1}, non-empty device_name) are appropriate for a probe surface.

---

## Scope Honesty

The report's non-claims are accurate and complete: no AMD GPU, no CPU fallback, no workload execution, no performance claims, no change to existing backends. The boundary between this goal and the next step (first HIPRT workload kernel) is clearly stated.

---

## Issues

None blocking. One cosmetic note: `hiprt_context_probe()` re-invokes `hiprt_version()` to populate the returned dict's `"version"` key, causing a second C call that is unnecessary since the shim already returns `api_version` directly. Harmless for a probe surface.

---

## Summary

The implementation is minimal, correctly bounded, passes on actual NVIDIA/CUDA hardware, degrades gracefully where HIPRT is absent, and makes no overclaims. Ready to proceed to the first HIPRT workload kernel goal.
