# Handoff: External Review Goal4251 v2.10 Internal Release-Prep Packet

Please perform an independent read-only review of:

- `docs/reports/goal4251_v2_10_internal_release_prep_packet_2026-06-09.md`
- `docs/reports/goal4248_current_public_docs_claim_boundary_scan_2026-06-09.md`
- `docs/reports/goal4249_major_performance_target_map_after_public_docs_scan_2026-06-09.md`
- `docs/reports/goal4250_post_docs_scan_pod_validation_2026-06-09.md`
- `src/rtdsl/current_major_performance_targets.py`
- tests:
  - `tests/goal4251_v2_10_internal_release_prep_packet_test.py`
  - `tests/goal4250_post_docs_scan_pod_validation_test.py`
  - `tests/goal4248_current_public_docs_claim_boundary_scan_test.py`
  - `tests/goal4219_major_performance_target_map_test.py`

Write your review to one of these paths:

- Claude: `docs/reviews/goal4252_claude_review_goal4251_v2_10_internal_release_prep_2026-06-09.md`
- Gemini: `docs/reviews/goal4253_gemini_review_goal4251_v2_10_internal_release_prep_2026-06-09.md`

Reviewer questions:

1. Does Goal4251 accurately summarize Goals4235, 4239, 4243, 4248, 4249, and
   4250 without overstating release readiness?
2. Are the blocked gates complete and correctly framed, especially release,
   broad speedup, whole-app, RayJoin superiority, paper reproduction, package
   install, true zero-copy, automatic partner selection, and AMD/HIPRT wording?
3. Does Goal4251 preserve the principle that RTDL is a generic language/runtime
   with explicit user-chosen partners, not an app library or hidden dispatcher?
4. Does the target map remain structurally non-authorizing after Goal4249?
5. Assuming no AMD claim is made, what evidence or wording remains before a
   formal release packet can be assembled?

Use one of these verdicts only:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

This is not a request to authorize release. It is a review of an internal
release-prep packet.
