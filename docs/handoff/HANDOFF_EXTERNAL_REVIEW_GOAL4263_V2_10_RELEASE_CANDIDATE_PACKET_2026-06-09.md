# Handoff: External Review Goal4263 v2.10 Release-Candidate Packet

Please perform an independent read-only review of the current v2.10
release-candidate packet draft after claim-wording closure.

Primary files:

- `docs/reports/goal4257_v2_10_release_candidate_packet_draft_2026-06-09.md`
- `docs/reports/goal4261_major_performance_target_map_after_claim_wording_closure_2026-06-09.md`
- `docs/reports/goal4262_exact_head_release_prep_pod_validation_2026-06-09.md`
- `docs/reports/goal4254_v2_10_public_claim_wording_candidate_2026-06-09.md`
- `docs/reports/goal4258_public_claim_wording_repair_closure_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`

Supporting reviews:

- `docs/reviews/goal4252_claude_review_goal4251_v2_10_internal_release_prep_2026-06-09.md`
- `docs/reviews/goal4253_gemini_review_goal4251_v2_10_internal_release_prep_2026-06-09.md`
- `docs/reviews/goal4255_claude_review_goal4254_public_claim_wording_2026-06-09.md`
- `docs/reviews/goal4256_gemini_review_goal4254_public_claim_wording_2026-06-09.md`
- `docs/reviews/goal4259_claude_review_goal4258_claim_wording_repair_closure_2026-06-09.md`
- `docs/reviews/goal4260_gemini_review_goal4258_claim_wording_repair_closure_2026-06-09.md`

Tests:

- `tests/goal4257_v2_10_release_candidate_packet_draft_test.py`
- `tests/goal4219_major_performance_target_map_test.py`
- `tests/goal4262_exact_head_release_prep_pod_validation_test.py`
- `tests/goal4254_v2_10_public_claim_wording_candidate_test.py`
- `tests/goal4258_public_claim_wording_repair_closure_test.py`
- `tests/goal4248_current_public_docs_claim_boundary_scan_test.py`

Write your review to one of these paths:

- Claude: `docs/reviews/goal4264_claude_review_goal4263_v2_10_release_candidate_packet_2026-06-09.md`
- Gemini: `docs/reviews/goal4265_gemini_review_goal4263_v2_10_release_candidate_packet_2026-06-09.md`

Reviewer questions:

1. Is the release-candidate packet now internally coherent after Goal4258-4262?
2. Does it preserve all blocked claims: release without user decision, public
   speedup, whole-app acceleration, broad RT-core, RTDL-beats-RayJoin, paper
   reproduction, package install, true zero-copy, automatic partner/backend
   selection, AMD/HIPRT, and app-specific native-engine logic?
3. Does the packet correctly say what remains: explicit user release decision,
   final consensus over the exact packet, and no AMD claim unless AMD hardware
   evidence is later produced?
4. Assuming no AMD/package-install/universal-speedup/whole-app claim is made,
   is any additional NVIDIA/OptiX measurement needed before the user can decide
   whether to release?
5. What exact change, if any, must happen before this can become a final release
   packet?

Use one of these verdicts only:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This review does not authorize release. It reviews release-candidate readiness.
