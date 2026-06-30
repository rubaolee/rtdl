# External Review Request: Goals4222-4225 Route Policy And Current Scale Packet

Date: 2026-06-09

Reviewer role: independent Claude/Gemini reviewer, distinct from Codex authoring.

Please review the Goal4222-4225 chain and write your review to one of these paths:

- Claude: `docs/reviews/goal4226_claude_review_goal4222_4225_route_policy_release_prep_2026-06-09.md`
- Gemini: `docs/reviews/goal4227_gemini_review_goal4222_4225_route_policy_release_prep_2026-06-09.md`

Use one of these verdicts only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

## Scope

Review these source artifacts:

- `docs/reports/goal4222_rtdbscan_blocked_vs_unblocked_profile_map_2026-06-09.md`
- `docs/reports/goal4222_rtdbscan_blocked_vs_unblocked_profile_map_rtx4000ada/summary.json`
- `scripts/goal4222_rtdbscan_blocked_vs_unblocked_profile_map.py`
- `tests/goal4222_rtdbscan_blocked_vs_unblocked_profile_map_test.py`
- `docs/reports/goal4223_rayjoin_public_cdb_contract_scale_map_2026-06-09.md`
- `docs/reports/goal4223_rayjoin_public_cdb_contract_scale_map_rtx4000ada/summary.json`
- `scripts/goal4223_rayjoin_public_cdb_contract_scale_map.py`
- `tests/goal4223_rayjoin_public_cdb_contract_scale_map_test.py`
- `src/rtdsl/current_major_performance_targets.py`
- `docs/reports/goal4224_major_performance_target_map_after_goal4223_2026-06-09.md`
- `tests/goal4219_major_performance_target_map_test.py`
- `docs/reports/goal4225_release_prep_current_scale_packet_2026-06-09.md`
- `docs/reports/goal4225_release_grade_current_scale_packet_rtx4000ada/current_scale_profile_packet.json`
- `tests/goal4225_release_prep_current_scale_packet_test.py`

## Questions To Answer

1. Goal4222: Does the blocked-vs-unblocked RT-DBSCAN profile map justify keeping `single_pass_candidate_root_rebased` as the current default and keeping the blocked grouped stream explicit/profile-specific?
2. Goal4223: Does the RayJoin public-CDB contract map justify the split policy: bounded PIP one-shot routes to Numba, while LSI and overlay scalar-count contracts route to prepared RTDL/OptiX?
3. Goal4224: Does the major performance target map correctly mark RayJoin route policy and RT-DBSCAN profile policy as internally covered, while keeping release-grade long-run evidence and AMD/HIPRT as remaining work?
4. Goal4225: Is the ten-app current scale packet valid current-state health evidence on RTX 4000 Ada, and does it avoid release/public-speedup/whole-app/broad-RT-core/paper-reproduction/true-zero-copy/automatic-partner/AMD claims?
5. Are the tests strong enough to catch the most likely overclaim or route-policy regressions?
6. What should be the next major engineering target before any formal major release packet?

## Required Boundary

This review must not authorize release action, public speedup wording, whole-app acceleration wording, broad RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic partner selection, AMD performance wording, or app-specific native-engine logic.

Recommended verdict if you find no defect: `accept-with-boundary`, because this is internal route-policy/current-scale evidence, not a release authorization.
