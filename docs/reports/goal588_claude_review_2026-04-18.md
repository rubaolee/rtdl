# Goal588 External Review — 2026-04-18

Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

---

## Claim Under Review

Goal588 adds a native adaptive C++ path for `point_nearest_segment`
(`native_adaptive_cpu_soa_min_distance_2d`) and claims correctness parity with
the Python reference plus a bounded local performance measurement.

---

## C++ Kernel (`rtdl_adaptive.cpp` lines 382–449)

**Correct.**

- `stage_segments_soa` reuses the existing SoA infrastructure; no new layout
  risk.
- `point_segment_distance_sq` uses the standard clamped-projection formula
  (`t = clamp(dot(p-a, d) / len_sq, 0, 1)`); handles zero-length segments
  correctly by falling back to point-to-point distance.
- Tie rule matches the stated spec: lower squared distance first; on equal
  distance (within `1e-14`), lower segment ID wins.
- Pre-allocates exactly `point_count` rows; emits only rows where a best
  segment was found; `segment_count == 0` correctly produces no output for
  any point.
- Error handling mirrors prior paths (null-guard, `bad_alloc`, generic
  exception). Output freed via `rtdl_adaptive_free_rows`.

No memory safety or logic errors observed.

---

## Python Binding (`adaptive_runtime.py`)

**Correct.**

- `_RtdlAdaptivePoint` and `_RtdlAdaptiveSegment` ctypes struct field
  order/types match the C declarations exactly.
- `argtypes`/`restype` for `rtdl_adaptive_run_point_nearest_segment` are
  fully declared (lines 744–754).
- `_support_row_with_runtime_mode` correctly patches the base compat record
  to `native=True` / `mode=ADAPTIVE_NATIVE_POINT_NEAREST_SEGMENT_MODE` when
  `adaptive_available()` (lines 468–470). The base record intentionally
  retains compat defaults as the fallback representation.
- `run_adaptive` routes to `_run_point_nearest_segment_native` when both the
  workload matches and the library is present (line 391); falls through to
  `run_cpu_python_reference` otherwise.

---

## Test (`goal588_adaptive_native_point_nearest_segment_test.py`)

**Adequate for the stated scope.**

- Verifies mode string promotes to `native_adaptive_cpu_soa_min_distance_2d`
  when the native library is present.
- Compares native output row-by-row against `run_cpu_python_reference` to
  7 decimal places for all floating-point fields.
- Test is skipped (not xfailed) when the library is not built, which is the
  correct policy for an optional native backend.
- Fixture is narrow (3 points × 3 segments) but covers point-projects-to-
  interior, point-projects-to-endpoint, and an oblique diagonal segment.

The performance report separately asserts `correctness parity: true` at 1024
× 2048, which corroborates the small-fixture test.

---

## Performance Evidence

**Appropriately bounded.**

| Path | Median (s) |
|---|---:|
| native C++ (`native_adaptive_cpu_soa_min_distance_2d`) | 0.005314 |
| `run_cpu_python_reference` | 0.591561 |

~111× speedup at 2M candidate pairs is credible for C++ brute-force vs.
Python brute-force with no interpreter overhead. The report makes no claim
about SciPy, FAISS, Embree, or vendor RT paths — that honesty is correct
given the scope.

---

## Boundary Compliance

Fixed-radius neighbors and KNN remain `ADAPTIVE_COMPAT_MODE` with `native=False`.
The 18-workload support matrix is unchanged except for the one promoted entry.
The Apple RT experiment dirt is acknowledged as out-of-scope.

---

## Issues Found

None blocking. One observation:

- The `_WORKLOADS_BY_PREDICATE` dict construction (lines 345–347) uses
  mutable tuple concatenation in a module-level loop; harmless at current
  scale but worth noting for future large matrix additions.

---

## Summary

The implementation is honest, the geometry is correct, the bindings match the
ABI, and the performance claim is scoped appropriately. Goal588 earns an
unconditional **ACCEPT**.
