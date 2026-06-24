# Call For Review: Phoenix V3 M45 Barnes-Hut Blocker Re-Audit

Date: 2026-06-23

Please critically review the M45 Barnes-Hut blocker re-audit.

Primary file:

- `docs/reports/phoenix_v3_m45_barnes_hut_blocker_reaudit_2026-06-23.md`

Required supporting files:

- `docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md`
- `docs/reports/phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_review_2026-06-23.raw.md`
- `docs/reviews/claude_phoenix_v3_m24_barnes_hut_prepared_query_residency_fix_followup_2026-06-23.raw.md`
- `docs/reports/phoenix_v3_barnes_hut_blocker_intake_m7_2026-06-22.md`
- `docs/rebuild/v3/phoenix_v3_m28_set_a_trunk_family_freeze_aggregate_tree_fused_vector_sum_2026-06-23.md`
- `docs/reports/phoenix_v3_m29_barnes_hut_v2_14_current_surface_classification_2026-06-23.md`
- `docs/reviews/claude_phoenix_v3_m29_barnes_hut_surface_classification_review_2026-06-23.raw.md`

Requested verdict labels:

- `accept_m45_barnes_hut_focused_fix_covered_move_to_remaining_blockers`
- `revise_m45_barnes_hut_still_active_coding_target`
- `revise_m45_missing_evidence_or_boundary`
- `reject_m45_barnes_hut_release_blocker_unresolved`

Review questions:

1. Does M45 correctly identify the frozen Barnes-Hut severe regression rows as
   OptiX node-coverage rows, while Embree rows are near parity?
2. Does M45 correctly distinguish the M24/M7 blocker-fix path from the M28/M29
   aggregate-tree fused runner capability path?
3. Is it fair to classify Barnes-Hut as focused-fix-covered for planning,
   pending next reviewed full-suite validation?
4. Is M45 correct that Barnes-Hut should not be the next active coding target?
5. Does M45 preserve the single-query prepare-cost boundary and avoid whole-app
   or broad V3-over-V2 claims?
6. What should the next active local engineering target be if Barnes-Hut is
   treated as covered-for-planning: LibRTS Set-B parity, another Set-A app-win
   shortfall, or something else?
7. Does M45 preserve all non-authorization boundaries?

Non-authorization to preserve:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
