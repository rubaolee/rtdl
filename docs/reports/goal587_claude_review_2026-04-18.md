# Goal587 Review Verdict

**ACCEPT**

Date: 2026-04-18

Reviewer: Claude (claude-sonnet-4-6)

---

## What was reviewed

- `src/native/rtdl_adaptive.cpp` — C++ segment-intersection kernel
- `src/rtdsl/adaptive_runtime.py` — Python dispatch and ctypes wiring
- `tests/goal587_adaptive_native_segment_intersection_test.py` — correctness test
- `docs/reports/goal587_adaptive_native_segment_intersection_2026-04-18.md` — perf report

---

## Correctness

**Math is correct.** `segment_intersection_point` (rtdl_adaptive.cpp:204–227) uses the standard
parametric 2D segment formula:

- Denominator is the 2D cross product `left_dx * right_dy - left_dy * right_dx`; parallel/degenerate
  case is guarded by `fabs(denom) < 1e-9`.
- `t` and `u` are computed correctly, both clamped to `[0,1]` before accepting the hit.
- Intersection point emitted as `left.x0 + t * left_dx`, `left.y0 + t * left_dy` — correct.

**SoA staging is correct.** `stage_segments_soa` precomputes direction vectors and axis-aligned
bounding boxes for the right (build) side once. The bounding-box early-reject in `bbox_overlap`
(rtdl_adaptive.cpp:190–202) is conservative and correct.

**Memory management is correct.** Output is `calloc`-allocated and freed via
`rtdl_adaptive_free_rows`; Python side frees in a `finally` block (adaptive_runtime.py:529–530),
ensuring no leak on exception.

**ctypes layout matches C structs exactly.** All `_RtdlAdaptiveSegment` and `_RtdlAdaptiveLsiRow`
field names, types, and ordering in Python mirror the C declarations.

**Mode promotion is honest.** `_support_row_with_runtime_mode` only sets `mode =
"native_adaptive_cpu_soa_2d"` and `native = True` when `adaptive_available()` returns true
(adaptive_runtime.py:444–448). The support matrix entry defaults to `cpu_reference_compat`/`False`
when the library is absent.

**One minor inefficiency (non-blocking):** `bbox_overlap` recomputes the left-segment bounding box
on every inner-loop iteration (rtdl_adaptive.cpp:194–197). These four values could be hoisted
outside the right-side loop. This is a missed micro-optimization, not a correctness issue.

---

## Test adequacy

The test (`Goal587AdaptiveNativeSegmentIntersectionTest`) is gated with
`@unittest.skipUnless(rt.adaptive_available(), ...)` — honest skip, not a false green.

It asserts:
1. Mode string is `"native_adaptive_cpu_soa_2d"` when library is present.
2. Native output matches `run_cpu_python_reference` row-for-row with `assertAlmostEqual` at 7
   decimal places.

The fixture (3 left × 3 right segments, 1 intersection expected) is small but exercises the
bbox-reject path (segment 12 is far away) and the degenerate non-intersecting pair (segments 2
and 11 are parallel or non-crossing). Sufficient for correctness parity; a larger combinatorial
fixture would strengthen confidence but is not required for this goal's scope.

---

## Performance evidence

Reported median timing on macOS, 1024 left × 2048 right (~2M candidate pairs, 2048 hits):

| Path | Median (s) |
|---|---:|
| native `native_adaptive_cpu_soa_2d` | 0.00552 |
| `run_cpu_python_reference` | 0.44626 |

Roughly 80× speedup. This is plausible: the C++ path eliminates the Python interpreter from the
inner loop and adds a bbox early-exit that rejects most candidate pairs. The report correctly
disclaims that this does not compare against Embree, OptiX, or other native backends, and that no
broad geometry-family claim is made.

---

## Scope honesty

The implementation does exactly what it claims: one new native adaptive path for
`segment_intersection`. All other 17 workloads remain in `cpu_reference_compat`. The boundary
statement in the perf report is accurate.

---

## Summary

The C++ math is correct, the Python wiring is safe and honest, the test provides meaningful parity
evidence, and the performance claim is bounded and plausible. The one inefficiency (left-bbox
recomputation in the inner loop) is advisory only. Goal587 may proceed.
