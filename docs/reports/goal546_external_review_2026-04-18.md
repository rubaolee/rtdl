# Goal 546 External Review

Date: 2026-04-18
Reviewer: Claude (claude-sonnet-4-6)
Verdict: **ACCEPT**

## Criteria Checklist

### 1. Honestly recognizes peer workloads

`_HIPRT_PEER_PREDICATES` (15 entries) matches the documented set exactly.
`_validate_hiprt_ray_hitcount_kernel` routes any predicate not in that set to
a `ValueError` ("unsupported predicate"), and any predicate in the peer set but
not yet implemented to `NotImplementedError` via `_unsupported_hiprt_peer_workload`.
Tests confirm `segment_intersection`, `fixed_radius_neighbors`, `bfs_discover`,
and `conjunctive_scan` all raise `NotImplementedError` with the predicate name in
the message. **Pass.**

### 2. Rejects unimplemented workloads without CPU fallback

`_unsupported_hiprt_peer_workload` always appends `"No CPU fallback is used."` to
the error string. The validation runs synchronously at the top of `run_hiprt` and
`prepare_hiprt`, before any `_hiprt_lib()` call, so the library is never loaded for
unimplemented predicates. `test_peer_2d_geometry_predicate_is_recognized_but_not_implemented`
and `test_prepare_hiprt_rejects_unimplemented_peer_predicate` both assert on this
string. **Pass.**

### 3. Preserves existing real HIPRT 3D hit-count path

`ray_triangle_hit_count_hiprt`, `PreparedHiprtRayTriangleHitCount3D`,
`prepare_hiprt_ray_triangle_hit_count`, `run_hiprt`, and `prepare_hiprt` are all
unchanged from goal 542/543. The 2D rejection branches correctly into
`_unsupported_hiprt_peer_workload` ("only Ray3DLayout and Triangle3DLayout are
implemented today") rather than reaching the live HIPRT calls. goal543 backend
tests (skipped locally, exercised on Linux) still target the 3D path. **Pass.**

## Minor Observations

`_validate_hiprt_ray_hitcount_kernel` is named as though it is ray-hitcount-specific,
but it now serves as the general HIPRT validation entry-point for all predicates.
This is a cosmetic issue only; the logic is correct.

`_HIPRT_GOAL_BY_PREDICATE` includes `"ray_triangle_hit_count": "Goal 549 for 2D,
Goal 548/542 for 3D"` even though 3D is already implemented. The 3D case never
reaches that entry (it passes the implemented check), so there is no behavioural
problem.

## Summary

The skeleton is honest: it names every peer workload, fails explicitly before backend
loading, quotes the owning goal, and states no CPU fallback. The real 3D HIPRT path
is untouched. Local (11 tests, OK) and Linux (16 tests, OK) validation results are
consistent with the code review. No blocking issues found.
