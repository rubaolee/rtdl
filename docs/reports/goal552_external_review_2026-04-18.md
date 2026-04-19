# Goal 552 External Review: HIPRT 2D Point-In-Polygon

Date: 2026-04-18
Reviewer: Claude (external AI review)

## Verdict: ACCEPT

No blockers found.

## Review Summary

### Correctness

**PiP algorithm** (`pointInPolygon2D`, lines 655–675): Standard even-odd ray-cast with `pointOnSegment2D` boundary promotion. Inclusive semantics are correct. The `(a.y - b.y) == 0.0f ? 1.0e-20f : ...` guard is unreachable in normal flow (horizontal edges are excluded by the crossing condition) but is harmless defensive code.

**Full-matrix semantics**: `RtdlPip2DKernel` initializes all `point_count * polygon_count` rows with `contains=0` before traversal and promotes to `contains=1` on confirmed containment. Initialization happens on GPU, consistent with the honesty boundary claim.

**Traversal loop**: `hiprtGeomCustomTraversalAnyHit` with a `while (!Finished) getNextHit()` loop correctly collects all containing polygons per point, not just the first hit. This matches the pattern established in the segment_intersection workload.

**Overflow guards**: Both `point_count > 2^32-1` and `point_count * polygon_count` size overflow are checked before GPU work begins.

### Python Dispatch

`lib.rtdl_hiprt_run_pip.argtypes` matches the C signature exactly (10 parameters: points ptr + size, polygons ptr + size, vertices ptr + size, rows_out ptr ptr + count ptr, error buf + size). Return value is checked; `_hiprt_lib().rtdl_hiprt_free_rows` is called in `finally`.

### Test Coverage

Three tests cover: (1) direct helper parity with CPU reference, (2) `rt.run_hiprt` parity with CPU reference, (3) empty inputs returning empty rows. All passing on Linux HIPRT hardware.

### Correctness Matrix

`point_in_polygon`: `parity=true`, `cpu_reference_row_count=2`, `hiprt_row_count=2`. No regressions; all 7 previously passing workloads remain PASS, fail=0.

## Limitations Acknowledged (Not Blockers)

- `exact=False` / `boundary_mode=inclusive` only; no `exact=True` path.
- `full_matrix` result mode only.
- AMD GPU behavior not validated (Linux NVIDIA GTX 1070 only).
- No performance claim made or expected.

## Status

ACCEPT. Implementation is correct within stated bounds. Honesty boundary is accurate.
