# Claude Review Handoff: Goal3372 Owner-Face CuPy Route Fixture Probe

Please perform an independent Claude review of Goal3372 in `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.

## Output Path

Write your review to:

`docs/reviews/goal3373_claude_review_owner_face_cupy_route_fixture_probe_2026-06-04.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Review commit `71a24af8` and these files:

- `scripts/goal3372_owner_face_cupy_route_fixture_probe.py`
- `docs/reports/goal3372_owner_face_cupy_route_fixture_probe_2026-06-04.json`
- `docs/reports/goal3372_owner_face_cupy_route_fixture_probe_2026-06-04.md`
- `tests/goal3372_owner_face_cupy_route_fixture_probe_test.py`
- relevant prior support:
  - `docs/reports/goal3369_owner_face_cupy_real_fixture_pipeline_2026-06-04.md`
  - `docs/reviews/goal3370_gemini_review_owner_face_cupy_pipeline_closure_2026-06-04.md`

## Review Questions

1. Does the script correctly run the composed CuPy owner-face selector+filter over the stored topology/incident artifacts without adding native/app-specific engine logic?
2. Does the JSON artifact honestly prove only the seven-point route fixture: owner faces match expected, recovered shape ids match exact, and claim boundaries are all false?
3. Is the commit/hardware provenance adequate for this internal evidence: commit `ef36541ed81695d79c39cdc8c08ac37fc154f4e9`, RTX A5000, CuPy 14.1.1?
4. Does the report avoid release, public speedup, RayJoin paper reproduction, broad RT-core speedup, true zero-copy, and RTDL-beats-RayJoin claims?
5. What remains before moving from stored route fixture to runtime-derived CDB topology/incident integration?

Be explicit that this is an independent Claude review distinct from Codex implementation and Gemini review.
