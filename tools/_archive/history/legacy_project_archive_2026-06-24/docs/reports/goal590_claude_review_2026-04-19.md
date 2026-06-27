# Goal590 External Review — Apple RT Native Segment Intersection

Date: 2026-04-19
Reviewer: Claude Sonnet 4.6
Verdict: **ACCEPT**

---

## What Was Reviewed

- `src/native/rtdl_apple_rt.mm` — new `rtdl_apple_rt_run_lsi` C++ function
- `src/rtdsl/apple_rt_runtime.py` — Python bindings and dispatch
- `tests/goal582_apple_rt_full_surface_dispatch_test.py` — updated test suite
- `docs/capability_boundaries.md` — updated capability statements
- `docs/reports/goal590_apple_rt_native_segment_intersection_2026-04-19.md` — implementation report

---

## Correctness

**Algorithm is sound.** Left segments are mapped to MPS rays with unnormalized direction vectors and `maxDistance = 1.000001f`. Because direction is not normalized, MPS returns a t-parameter value, not a world-space distance. The slack `1.000001` keeps endpoint hits in the candidate set; the subsequent analytic `segment_intersection_point` filter at line 594 enforces exact RTDL bounds in double precision. This two-phase candidate/confirm pattern is the correct approach.

**Quadrilateral extrusion is correct.** Each right segment is extruded ±1.0 in z into a 4-vertex quad for `MPSQuadrilateralAccelerationStructure`. All left-ray origins are at z=0, so the z=0 plane reliably bisects the extruded quad. The quad's xy endpoints match the right segment's endpoints.

**Output order is left-major.** `rows_by_left` (a vector-of-vectors indexed by left_index) collects hits per left segment, then flattens in order. This matches `lsi_cpu` left-major semantics.

**Invalid segments are skipped.** `valid_segment_ray` guards both sides; zero-length segments produce no output.

**FFI struct layout is consistent.** `RtdlSegment` in C++ has no `__attribute__((packed))`, and `_RtdlSegment` in Python has no `_pack_ = 1`. Both use natural alignment (4-byte pad after `uint32_t id` before the first `double`), so layout matches on 64-bit macOS. The asymmetry with `RtdlRay3D`/`RtdlTriangle3D` (which are packed on both sides) is not a bug — both sides of each struct agree.

---

## Testing

`test_segment_intersection_native_matches_cpu_reference` (line 214) uses 3 left × 3 right segments with multiple intersections and an endpoint hit. It verifies row count, row order, and field values against `run_cpu_python_reference` via `_assert_rows_almost_equal`. The direct `segment_intersection_apple_rt` helper is also exercised. The test is meaningful and not a trivial case.

The predicate mode test verifies `apple_rt_predicate_mode("segment_intersection")` returns `"native_mps_rt"`. The 18-predicate dispatch smoke test at line 244 confirms segment_intersection routes correctly through `run_apple_rt`.

---

## Documentation Honesty

`capability_boundaries.md` (lines 266–277) accurately states: Goal590 adds native Apple MPS RT for 2D segment_intersection via extruded quadrilaterals and analytic refinement; broader 2D geometry and other paths remain `cpu_reference_compat`. No speedup claim is made.

The implementation report is candid that the native path is slower than CPU reference (0.084 s vs 0.011 s median) because a new MPS BVH is rebuilt per right segment on a 128×128 smoke workload. The overhead is correctly attributed and no performance claim appears in docs.

---

## Minor Observations (Non-blocking)

1. Variable names `rays` and `triangles` in `run_apple_rt` (lines 437–438) hold left/right segments for the `segment_intersection` branch — misleading but functionally correct.
2. `rows.reserve(std::min(left_count * right_count, 1024uz))` (line 602) is a reserve hint that caps at 1024 for large inputs. This is not a capacity cap — `std::vector` will grow past 1024 — so it does not affect correctness.

---

## Verdict

**ACCEPT.** The native Apple MPS 2D segment_intersection is correctly implemented (candidate MPS filter + analytic double-precision confirmation), left-major ordered, endpoint-inclusive, tested against CPU reference with non-trivial cases, and documented without overclaiming speedup or parity.
