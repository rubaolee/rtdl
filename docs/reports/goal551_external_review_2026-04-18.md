# Goal 551 External Review: HIPRT 2D Ray/Triangle Hit Count

Date: 2026-04-18
Reviewer: Claude Sonnet 4.6 (external AI review)

## Verdict: ACCEPT

## Evidence Checked

- `docs/reports/goal551_hiprt_ray_triangle_2d_2026-04-18.md` — implementation summary and test output
- `docs/reports/goal551_hiprt_correctness_matrix_linux_2026-04-18.json` — pass=6, fail=0, no HIPRT-unavailable
- `tests/goal551_hiprt_ray_triangle_2d_test.py` — 3 tests covering direct helper, `run_hiprt` dispatch, and empty-triangle edge case
- `src/native/rtdl_hiprt.cpp` — native HIPRT kernel and intersection function
- `src/rtdsl/hiprt_runtime.py` — ctypes dispatch and `run_hiprt` layout-pair routing

## Findings

**Correctness of segment encoding:** The kernel encodes the finite ray as `direction = (dx*tmax, dy*tmax)` with `maxT=1.0`, making `origin + direction` equal to the ray endpoint. `finiteRayHitsTriangle2D` uses `origin` and `origin + direction` as the two finite endpoints — this is correct.

**Intersection logic:** `finiteRayHitsTriangle2D` checks point-in-triangle for both endpoints, then tests the segment against all three triangle edges via `finiteSegmentIntersectsSegment2D`. The parametric segment-segment test correctly uses `t ∈ [0,1]` and `u ∈ [0,1]`. Degenerate/parallel edges are handled by the `|denom| < 1e-7` guard returning false, matching `exact=False` CPU behavior.

**Custom intersection function:** `intersectRtdlTriangle2D` reads the pre-loaded triangle data via `primID`, tests intersection, and sets `hit.t = 0.0f` on accept — the standard HIPRT any-hit counting pattern used in the existing 3D path.

**Dispatch routing:** `run_hiprt` correctly gates on `layout_pair == ("Ray2D", "Triangle2D")` to reach the new 2D path; 3D layouts continue on the existing path.

**Test coverage:** All three test cases pass on Linux HIPRT hardware. Empty-triangle case returns zero counts. CPU-reference parity is validated for the main case.

**No blockers found.**

## Limitations (not blockers)

- AMD GPU path unvalidated (acknowledged in honesty boundary).
- `exact=True` predicate not supported (out of scope for this goal).
