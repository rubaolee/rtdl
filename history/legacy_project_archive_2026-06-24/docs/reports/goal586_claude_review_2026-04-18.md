# Goal586 Review — Claude Sonnet 4.6

**Verdict: ACCEPT**

Date: 2026-04-18

Reviewer: Claude Sonnet 4.6 (automated external review)

---

## Summary

Goal586 honestly adds the first native adaptive path for 3D ray/triangle hit-count.
The C++ kernel is algorithmically correct, the Python bindings are correctly typed,
and the performance claim is real and properly bounded.

---

## Correctness

**Algorithm:** `finite_ray_hits_triangle_3d` is a faithful Möller–Trumbore implementation:
- p-vector = cross(D, e2); det = dot(e1, p) — standard determinant form
- u = dot(T, p) / det, checked in [0, 1]
- q-vector = cross(T, e1); v = dot(D, q) / det, checked ≥ 0 and u+v ≤ 1
- t = dot(e2, q) / det, checked in [0, tmax]

No sign errors, no axis swaps, no missed condition. ✓

**SoA staging:** Edge vectors e1 = v1−v0, e2 = v2−v0 are precomputed correctly. ✓

**ctypes struct layout:** `_RtdlAdaptiveRay3D` (uint32 + 7 f64) and
`_RtdlAdaptiveTriangle3D` (uint32 + 9 f64) follow C alignment rules; ctypes
inserts the 4-byte pad after the id field automatically, matching the C layout. ✓

**Memory safety:** `calloc(ray_count == 0 ? 1 : ray_count, ...)` avoids zero-count
UB; freed via `std::free` in a Python `finally` block matching the C allocator. ✓

**Fallback integrity:** When the library is absent, `adaptive_available()` returns
False, `run_adaptive` falls back to `run_cpu_python_reference`, and no native-mode
claim is surfaced. ✓

**Test:** 3-ray × 3-triangle parity check against the reference path passes.
The fixture is small but adequate — it exercises the mode-string contract and
numeric equality against a trusted reference. The skip decorator correctly gates the
test on library presence.

---

## Performance Evidence

| Path | Median (s) |
| --- | ---: |
| `native_adaptive_cpu_soa_3d` (C++) | 0.002295 |
| `run_cpu_python_reference` (Python) | 0.239230 |

~104× speedup at 512 rays × 1024 triangles (524 288 candidate pairs).

The report correctly qualifies what this does and does not prove:
- **Does prove:** Python is removed from the hot loop.
- **Does not prove:** broad 18-workload speedup, or parity with Embree/Apple RT/OptiX/Vulkan/HIPRT.

Evidence is bounded and honest. ✓

---

## Minor Issues (non-blocking)

1. **`rtdl_adaptive_free_rows` missing `RTDL_ADAPTIVE_EXPORT`** (line 48 of `rtdl_adaptive.cpp`).
   The other two exported symbols carry the attribute; this one does not.
   Not a runtime bug — the Makefile uses `-O3 -shared -fPIC` with no
   `-fvisibility=hidden`, so the symbol is visible by default. But the
   inconsistency is a latent defect: adding `-fvisibility=hidden` in a future
   hardening pass would silently break `rtdl_adaptive_free_rows`.
   **Recommendation:** add `RTDL_ADAPTIVE_EXPORT` to `rtdl_adaptive_free_rows`.

2. **Test fixture exercises only 3 rays and 3 triangles.** Edge cases — degenerate
   triangles (zero-area), rays parallel to triangle plane, rays at exactly tmax —
   are not covered. Acceptable for a first native slice; should be addressed in a
   follow-on correctness gate before the backend is used in production workloads.

---

## Scope Check

Goal586 claims native adaptive support only for `ray_triangle_hit_count_3d`.
The `_support_row_with_runtime_mode` function upgrades exactly that one workload;
the other 17 remain at `cpu_reference_compat` with `native=False`.
Closest-hit is not claimed. Scope boundary is respected. ✓

---

## Decision

ACCEPT. The implementation is algorithmically correct, the bindings are safe, the
performance claim is real and properly bounded, and the scope boundary is honest.
The missing `RTDL_ADAPTIVE_EXPORT` on `rtdl_adaptive_free_rows` should be fixed
before `-fvisibility=hidden` is ever added to the build flags.
