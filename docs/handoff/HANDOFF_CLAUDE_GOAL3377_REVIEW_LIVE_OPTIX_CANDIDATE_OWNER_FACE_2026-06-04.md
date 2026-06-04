# Claude Review Handoff: Goal3376 Live OptiX Candidate Owner-Face Route Probe

Please perform an independent Claude review of Goal3376 in `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.

## Output Path

Write your review to:

`docs/reviews/goal3377_claude_review_live_optix_candidate_owner_face_route_probe_2026-06-04.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Review commits:

- `ddc6962c` — adds `scripts/goal3376_owner_face_cupy_optix_candidate_route_probe.py`
- `5d486542` — records the Goal3376 artifact/report/test

Review these files:

- `scripts/goal3376_owner_face_cupy_optix_candidate_route_probe.py`
- `docs/reports/goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.json`
- `docs/reports/goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.md`
- `tests/goal3376_owner_face_cupy_optix_candidate_route_probe_test.py`
- prior stepping stones:
  - `docs/reviews/goal3373_claude_review_owner_face_cupy_route_fixture_probe_2026-06-04.md`
  - `docs/reports/goal3374_owner_face_cupy_runtime_cdb_route_probe_2026-06-04.md`

## Review Questions

1. Does Goal3376 genuinely replace stored candidate-row input with RTDL/OptiX live `candidate_device_columns(...)` output?
2. Does the script keep native engine logic generic and app-agnostic, with owner-face policy remaining in the app/Python/CuPy continuation?
3. Does the artifact honestly show the seven known boundary-extra points: live candidates include extras, owner-face continuation removes them, recovered shapes match exact?
4. Are the provenance fields and tests sufficient for this internal stage: commit `ddc6962c4c23d4bd9091f487d35f029b7b042ef7`, RTX A5000, CuPy 14.1.1, OptiX candidate row count 1429, selected candidate row count 26?
5. Are all claim boundaries safe: no release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true-zero-copy, or default-route claims?
6. What remains before route-scale promotion: removing the seven-point mask, deriving/validating owner-face priority policy for all points, default route selection, or native lowering?

Be explicit that this is an independent Claude review distinct from Codex implementation. Do not authorize release or public claims.
