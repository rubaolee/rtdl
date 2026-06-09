# Handoff: External Review Goal4254 v2.10 Public Claim Wording Candidate

Please perform an independent read-only review of:

- `docs/reports/goal4254_v2_10_public_claim_wording_candidate_2026-06-09.md`
- `docs/reports/goal4251_v2_10_internal_release_prep_packet_2026-06-09.md`
- `docs/reports/goal4248_current_public_docs_claim_boundary_scan_2026-06-09.md`
- `docs/reports/goal4249_major_performance_target_map_after_public_docs_scan_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- tests:
  - `tests/goal4254_v2_10_public_claim_wording_candidate_test.py`
  - `tests/goal4251_v2_10_internal_release_prep_packet_test.py`
  - `tests/goal4248_current_public_docs_claim_boundary_scan_test.py`
  - `tests/goal4219_major_performance_target_map_test.py`

Write your review to one of these paths:

- Claude: `docs/reviews/goal4255_claude_review_goal4254_public_claim_wording_2026-06-09.md`
- Gemini: `docs/reviews/goal4256_gemini_review_goal4254_public_claim_wording_2026-06-09.md`

Reviewer questions:

1. Is the candidate short description accurate for current v2.10 RTDL?
2. Are all allowed claims scoped tightly enough to reviewed internal evidence?
3. Are all blocked claims explicit enough, especially package install, universal
   speedup, broad RT-core speedup, whole-app acceleration, RayJoin superiority,
   paper reproduction, true zero-copy, automatic partner selection, AMD/HIPRT,
   and app-specific native-engine logic?
4. Does the candidate front-page paragraph read clearly to learners without
   inviting overclaim?
5. What exact wording, if any, must change before this can become part of a
   formal release packet?

Use one of these verdicts only:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is a wording review only. It does not authorize release.
