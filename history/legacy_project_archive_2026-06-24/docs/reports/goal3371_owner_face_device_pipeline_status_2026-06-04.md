# Goal3371: Owner-Face Device Pipeline Status

Date: 2026-06-04

Status: internal v2.8 status packet. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Summary

The owner-face topology chain has moved from a Python row/column reference into an internal CuPy device-column continuation chain:

1. Goal3349-3356: explicit owner-face priority pipeline contract, rank-signal derivation, columnar selection, columnar filtering, and status packet.
2. Goal3357/3360: Claude review and closure review.
3. Goal3358-3359: seven-point real fixture and filter-policy closure.
4. Goal3361: validator hardening for missing-topology and face-presence policy.
5. Goal3362: CuPy membership filter continuation.
6. Goal3363-3364: Claude review and filter gap closure.
7. Goal3365: CuPy owner-face selector continuation.
8. Goal3366-3368: Claude review and selector gap closure.
9. Goal3367: composed CuPy selector plus membership filter pipeline.
10. Goal3369: composed CuPy pipeline over the seven known county mismatch points.
11. Goal3370: Gemini review requested for Goal3367-3369.

## Current Device Surface

The current optional device-column helpers are:

- `select_owner_faces_from_incident_candidate_columns_with_priority_cupy(...)`
- `filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(...)`
- `run_closed_shape_owner_face_priority_membership_pipeline_cupy(...)`

The helpers consume generic columns only:

- point ids,
- face ids,
- incident counts,
- caller-supplied priorities,
- candidate point/shape ids,
- topology shape/face ids and face-presence gates.

The native engine still does not infer owner-face priority or application ownership.

## Evidence

Pod: `root@69.30.85.203 -p 22057`

Hardware:

- GPU: `NVIDIA RTX A5000`
- CuPy: `14.1.1`

Key pod runs:

| Goal | Scope | Result |
| --- | --- | --- |
| Goal3362 | CuPy filter focused chain | `Ran 15 tests in 8.593s` / `OK` |
| Goal3364 | filter review-gap closure focused chain | `Ran 20 tests in 0.743s` / `OK` |
| Goal3364 | full owner-face family | `Ran 80 tests in 0.766s` / `OK` |
| Goal3365 | CuPy selector focused chain | `Ran 26 tests in 1.230s` / `OK` |
| Goal3365 | full owner-face family | `Ran 85 tests in 0.687s` / `OK` |
| Goal3367 | composed pipeline focused chain | `Ran 30 tests in 0.830s` / `OK` |
| Goal3367 | full owner-face family | `Ran 89 tests in 0.760s` / `OK` |
| Goal3368 | selector review-gap closure focused chain | `Ran 24 tests in 0.850s` / `OK` |
| Goal3368 | full owner-face family | `Ran 94 tests in 0.832s` / `OK` |
| Goal3369 | seven-point real fixture focused chain | `Ran 14 tests in 0.765s` / `OK` |
| Goal3369 | full owner-face family | `Ran 96 tests in 0.782s` / `OK` |

## Review State

- `docs/reviews/goal3357_claude_review_owner_face_columnar_pipeline_2026-06-04.md`: `accept-with-boundary`.
- `docs/reviews/goal3360_claude_review_owner_face_columnar_closure_2026-06-04.md`: `accept`.
- `docs/reviews/goal3363_claude_review_owner_face_cupy_continuation_2026-06-04.md`: `accept-with-boundary`.
- `docs/reviews/goal3366_claude_review_owner_face_cupy_selection_continuation_2026-06-04.md`: `accept-with-boundary`.
- Goal3370 Gemini review of Goal3367-3369 is requested and pending.

## Still Blocked

The current chain is useful internal device-continuation evidence, but it is not a default device-lowered/native path.

Still blocked before promotion:

- fresh external review of Goal3367-3369,
- larger-scale performance measurements,
- decision on whether selection/filter should remain partner continuation or receive a native generic lowering,
- proof that all app-facing routes use explicit caller policy and cannot bypass the contract,
- release or public performance wording,
- RayJoin paper reproduction wording,
- RTDL-beats-RayJoin wording,
- broad RT-core speedup wording,
- true zero-copy wording.

## Next Engineering Candidates

1. Ingest Goal3370 Gemini review when it lands.
2. Add a route-level integration harness that uses the composed CuPy pipeline inside the current RayJoin/CDB count path while preserving the claim boundary.
3. Measure whether the composed device pipeline reduces host-side owner-face continuation overhead on the real fixture and a larger synthetic topology fixture.
4. Only after review and measurements, decide whether a generic native lowering is justified.
