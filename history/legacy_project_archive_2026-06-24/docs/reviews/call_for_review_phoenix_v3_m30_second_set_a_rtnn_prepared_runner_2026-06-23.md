# Call For Review: Phoenix V3 M30 Second Set-A Candidate RTNN Prepared Runner

Date: 2026-06-23

Please critically review the M30 candidate report:

`docs/reports/phoenix_v3_m30_second_set_a_candidate_rtnn_prepared_runner_2026-06-23.md`

Primary evidence:

`docs/rebuild/v3/evidence/phoenix_v3_rtnn_prepared_execution_runner_repeat50_20260622/`

Primary evidence report:

`docs/rebuild/v3/phoenix_v3_rtnn_prepared_execution_runner_repeat50_pod_evidence_2026-06-22.md`

Prior result review:

`docs/reviews/kepler_phoenix_v3_rtnn_step2_result_review_2026-06-22.md`

Prior Claude repeat50 wording review:

`docs/reviews/claude_phoenix_v3_rtnn_prepared_repeat50_amortization_review_2026-06-21.md`

M28/M29 current first-family chain:

`docs/reviews/codex_claude_phoenix_v3_m28_set_a_trunk_family_freeze_2ai_consensus_2026-06-23.md`

`docs/reviews/codex_claude_phoenix_v3_m29_barnes_hut_surface_classification_2ai_consensus_2026-06-23.md`

Post-M22 context that must not be overridden:

`docs/reports/phoenix_v3_m20_scorecard_sync_after_triangle_m19_2026-06-22.md`

`docs/reviews/codex_claude_phoenix_v3_m20_scorecard_sync_2ai_consensus_2026-06-22.md`

`docs/reviews/call_for_review_phoenix_v3_m22_all_app_result_facts_only_2026-06-23.md`

`docs/reports/phoenix_v3_m23_rayjoin_shape_pair_fix_2026-06-23.md`

`docs/reports/phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_2026-06-23.md`

`docs/reviews/codex_claude_phoenix_v3_m27_librts_aabb_set_b_triage_and_cold_optix_retain_fix_2ai_consensus_2026-06-23.md`

## Requested Verdict Labels

Use exactly one:

- `accept_m30_rtnn_as_second_set_a`
- `accept_with_amendments`
- `blocked_needs_focused_rerun`
- `reject_not_second_set_a`

## Questions

1. Does the 2026-06-22 RTNN prepared-execution runner repeat50 evidence qualify
   as the second true Set-A runtime-trunk family after the M28/M29 Barnes-Hut
   family?
2. Is it correct to use the productized-runner evidence rather than the older
   2026-06-21 CuPy-only amortization row as the controlling M30 evidence?
3. Are the material numbers interpreted correctly: runner vs legacy
   cold-plus-query `1.358329x`, runner vs legacy runner wall `1.370176x`, and
   runner vs legacy hot query `0.988781x`?
4. Are the repeat50, CuPy-reference, provenance, and no-single-shot boundaries
   strong enough?
5. Should M30 avoid new POD time and accept the existing same-hardware evidence,
   or does provenance/scope require a focused rerun?
6. Does the M20/M22/M27 context change the meaning of M30? In particular, does
   accepting RTNN as a focused Set-A family still leave the M22 non-release
   result and remaining blockers intact?
7. Does this decision still forbid all-app, release, public speedup, broad
   V3-over-V2, true-zero-copy, and V4 work?

## Required Output

Save your review to:

`docs/reviews/claude_phoenix_v3_m30_second_set_a_rtnn_prepared_runner_review_2026-06-23.raw.md`

Include:

- one verdict label;
- blocking findings, if any;
- required amendments, if any;
- explicit answers to the seven questions;
- a non-authorization block stating that your review authorizes no release, no
  all-app run, no public speedup claim, no broad V3-over-V2 claim, no RT-core
  speedup claim, no single-shot RTNN speedup claim, no true-zero-copy claim, no
  automatic partner-selection claim, and no V4 work.
