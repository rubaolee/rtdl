# Claude Review Handoff: Goal3378 Owner-Face All-Point Negative Probe

Please perform an independent Claude review of Goal3378 in `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.

## Output Path

Write your review to:

`docs/reviews/goal3379_claude_review_owner_face_route_scale_negative_probe_2026-06-04.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Review commits:

- `75876b18` — adds `scripts/goal3378_owner_face_all_point_priority_negative_probe.py`
- `a494b68b` — records the Goal3378 artifact/report/test

Review these files:

- `scripts/goal3378_owner_face_all_point_priority_negative_probe.py`
- `docs/reports/goal3378_owner_face_all_point_priority_negative_probe_2026-06-04.json`
- `docs/reports/goal3378_owner_face_all_point_priority_negative_probe_2026-06-04.md`
- `tests/goal3378_owner_face_all_point_priority_negative_probe_test.py`
- prior positive step:
  - `docs/reports/goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.md`
  - `docs/reviews/goal3377_claude_review_live_optix_candidate_owner_face_route_probe_2026-06-04.md`

## Review Questions

1. Does Goal3378 honestly test and reject the all-point `incident_chain_length_rank` policy rather than trying to promote it?
2. Does the negative artifact support the conclusion: exact rows 1417, live candidates 1429, filtered rows 1007, missing exact rows 410, extras 0, `matches_exact: false`?
3. Does the script keep the experimental priority policy in caller/Python logic and avoid adding app-specific native engine behavior?
4. Are the report/test boundaries safe: no release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true-zero-copy, or native default route claims?
5. Is the proposed next direction reasonable: selective ambiguity-set filtering or stronger boundary-topology policy, rather than filtering every candidate row?

Be explicit that this is an independent Claude review distinct from Codex implementation. Do not authorize release or public claims.
