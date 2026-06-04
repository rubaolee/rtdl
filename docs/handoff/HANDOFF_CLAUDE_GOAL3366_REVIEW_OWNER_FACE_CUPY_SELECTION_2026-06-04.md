# Claude Review Handoff: Goal3365 Owner-Face CuPy Selection Continuation

Please perform an independent Claude review of the Goal3365 owner-face CuPy selection continuation in `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.

## Output Path

Write your review to:

`docs/reviews/goal3366_claude_review_owner_face_cupy_selection_continuation_2026-06-04.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Review commit `6196c991` and these files:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `tests/goal3365_owner_face_cupy_selection_continuation_test.py`
- `docs/reports/goal3365_owner_face_cupy_selection_continuation_2026-06-04.md`
- supporting prior review/closure:
  - `docs/reviews/goal3363_claude_review_owner_face_cupy_continuation_2026-06-04.md`
  - `docs/reports/goal3364_owner_face_cupy_review_gap_closure_2026-06-04.md`

## Review Questions

1. Does `select_owner_faces_from_incident_candidate_columns_with_priority_cupy(...)` preserve the Python selector's core semantics: unique max wins, tied max requires explicit priority, missing/tied priority fails closed by default, and `emit_ambiguous` remains explicit?
2. Are the numeric `selection_status_code` outputs and label map a valid device-column substitute for Python status strings without hiding semantics from downstream callers?
3. Are the duplicate incident/priority pair restrictions, dense int64 pair-key overflow guard, and CuPy empty-mask guard sufficient for this internal continuation stage?
4. Does the contract/export/report wording keep the path app-agnostic and avoid release, RayJoin reproduction, RT-core, true zero-copy, public speedup, or RTDL-beats-RayJoin claims?
5. Is the pod evidence sufficient for this internal device-continuation step: RTX A5000, CuPy 14.1.1, focused `Ran 26 tests in 1.230s OK`, full owner-face family `Ran 85 tests in 0.687s OK`?
6. What must be fixed before the owner-face selection/filter pair can be promoted toward a default device-lowered path?

## Required Boundaries

This review must not authorize release, public speedup wording, RayJoin paper reproduction wording, broad RT-core speedup wording, RTDL-beats-RayJoin wording, or true zero-copy wording.

Be explicit that this is an independent Claude review distinct from Codex implementation.
