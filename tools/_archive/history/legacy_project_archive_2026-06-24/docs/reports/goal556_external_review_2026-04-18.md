# External Review: Goal 556 — HIPRT Overlay Compose

**Date:** 2026-04-18
**Reviewer:** Claude (external AI review)
**Verdict:** ACCEPT

---

## Summary

Goal 556 adds a real HIPRT traversal path for `overlay_compose` on `Polygon2DRef` inputs, closing the last 2D-only correctness-matrix gap for v0.9. The implementation is correct within its stated scope and the honesty boundary is accurately described.

---

## What was reviewed

- `docs/reports/goal556_hiprt_overlay_2026-04-18.md` — design and validation narrative
- `src/native/rtdl_hiprt.cpp` — device kernel and host dispatch
- `src/rtdsl/hiprt_runtime.py` — Python FFI layer
- `tests/goal556_hiprt_overlay_test.py` — test suite
- `docs/reports/goal556_hiprt_correctness_matrix_linux_2026-04-18.json` — correctness matrix

---

## Findings

### Correctness

The device kernel (`RtdlOverlay2DKernel`) is correct. Each left-polygon thread:

1. Pre-fills its row slice with `{left_id, right_id, 0, 0}` for all right polygons, ensuring every output row is initialized even if the traversal misses a candidate.
2. Fires a point-probe ray through the AABB BVH of right polygons.
3. For each visited candidate, calls `polygonsHaveLsi2D` (edge-pair exhaustive scan) and `pointInPolygon2D` (winding-number + boundary check) to compute `requires_lsi` and `requires_pip`.

The broad-AABB strategy guarantees that every left first-vertex falls inside every right polygon AABB, so the traversal visits all L×R pairs. The pre-fill + traversal combination is sound: non-visited slots correctly keep their zero values, and visited slots are updated in place.

`polygonsHaveLsi2D`, `segmentsIntersect2D`, `pointInPolygon2D`, and `pointOnSegment2D` all match the CPU reference semantics. The collinear/boundary cases in `segmentsIntersect2D` (orient + pointOnSegment fallbacks) are correct.

The Python FFI (`overlay_compose_hiprt`) correctly declares the `rtdl_hiprt_run_overlay` argtypes, encodes polygon refs and interleaved vertex arrays, and reads back the output struct fields.

Correctness matrix: **13 pass, 0 fail** — `overlay_compose` is newly passing.

### Design — noted but not blockers

**Broad-phase is O(L×R) by construction.** Right polygon AABBs are inflated to cover every left first-vertex, so all pairs are always visited. The report explicitly acknowledges this is correctness-first, not performance-forward. Acceptable for v0.9; a spatial filter on right AABBs would be the natural next step for performance.

**Vertex precision is float on device.** `RtdlHiprtVertex2DDevice` stores `float x, y` even though the public API takes `double`. This is consistent with every other 2D HIPRT workload in the codebase. No new regression introduced here.

**Test geometry is axis-aligned squares only.** The three tests cover disjoint, contained, and overlapping pairs. Non-axis-aligned polygons and degenerate cases (collinear edges, coincident vertices) are exercised indirectly via the CPU reference comparator. Adequate for a correctness-parity goal; further geometric variety is a nice-to-have, not a requirement.

**AMD GPU coverage is unverified.** Validation was performed on GTX 1070 (Orochi CUDA mode). This is consistent with the broader project state and accurately disclosed.

### No blockers found

All three tests pass on Linux HIPRT build. The implementation correctly maps through the full stack: Python API → ctypes FFI → host dispatch → device kernel. The honesty boundary in the report matches the code.

---

## Conclusion

ACCEPT. Goal 556 delivers correct HIPRT `overlay_compose` parity with the CPU reference. The broad-candidate design is an intentional, documented trade-off. No blocking issues.
