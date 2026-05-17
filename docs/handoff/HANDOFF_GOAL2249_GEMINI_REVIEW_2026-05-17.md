# Handoff: Gemini Review For Goal2248/2249 Prepared Closed-Shape Membership

Please perform an independent read-only review of the latest pushed RTDL main
state plus local Goal2249 evidence files.

## Context

Goal2248 added a generic prepared OptiX closed-shape membership primitive:

- `rtdl_optix_prepare_point_closed_shape_membership_2d`
- `rtdl_optix_run_prepared_point_closed_shape_membership_2d`
- `rtdl_optix_destroy_prepared_point_closed_shape_membership_2d`
- Python wrapper:
  `prepare_point_closed_shape_membership_2d_optix(...)` /
  `PreparedOptixPointClosedShapeMembership2D.run(...)`

Goal2249 records the clean pushed-commit pod timing for the RayJoin same-query
PIP learner workload using the prepared primitive:

- Commit: `9e8c60ef6ae6a1311940b76861fc9a665a52dcc5`
- Artifact:
  `docs/reports/goal2249_rayjoin_pip_prepared_closed_shape_same_query_pod_2026-05-17.json`
- Report:
  `docs/reports/goal2249_rayjoin_pip_prepared_closed_shape_pod_evidence_2026-05-17.md`
- Test:
  `tests/goal2249_rayjoin_pip_prepared_closed_shape_pod_evidence_test.py`

## Review Questions

1. Does the native ABI remain app-agnostic, using point/closed-shape/membership
   vocabulary rather than RayJoin/PIP/polygon app-specific names?
2. Does the Python runner correctly route same-query PIP OptiX through the
   prepared closed-shape membership path while preserving the RayJoin row
   contract at the Python layer?
3. Is the pod evidence correctly tied to the pushed commit and does it support
   only the narrow claim made in the report?
4. Does the boundary avoid overclaiming full RayJoin reproduction, RTDL beating
   RayJoin, paper-scale speedup, broad PIP acceleration, or v2.0 release
   readiness?

## Expected Output

Write the review to:

`docs/reviews/goal2250_gemini_review_goal2248_2249_prepared_closed_shape_2026-05-17.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Please state explicitly that this is an independent Gemini review distinct from
Codex, and do not mutate source files outside the requested review document.
