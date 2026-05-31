# Call For External Review: Goal2868 v2.5 Last-Day Work Since Claude Reviews

Please review the v2.5 work completed after the fresh Claude v2.5 status/design
reviews were received and incorporated.

This is a broad audit request, not a request to rubber-stamp release. The
reviewer should be critical and should look for ordering mistakes, claim
boundary leaks, stale assumptions, app-specific engine leakage, benchmark
evidence gaps, and places where metadata says more than the code or artifacts
prove.

## Review Output Path

Write your review to one of these paths, depending on reviewer:

- Claude:
  `docs/reviews/goal2868_claude_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`
- Gemini:
  `docs/reviews/goal2868_gemini_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`
- Copilot:
  `docs/reviews/goal2868_copilot_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`
- Other reviewer:
  `docs/reviews/goal2868_<reviewer>_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`

## Scope

Primary scope:

- Start anchor: `3f8b1d5b Goal2773 record Claude review intake`
- End anchor: `fbe28476 Goal2867 audit v2.5 front door bypasses`
- Practical command:
  `git log --oneline 3f8b1d5b..fbe28476`

The reviewer should treat this as the last-day v2.5 implementation burst after
Claude's critical review intake, especially the work from Goal2773 through
Goal2867.

## Review Anchors

Start by reading:

- `docs/reviews/goal2773_claude_review_v2_5_status_next_goals_2026-05-31.md`
- `docs/reports/goal2773_claude_review_intake_and_revised_v2_5_plan_2026-05-31.md`
- `docs/reports/goal2773_v2_5_status_next_goals_review_packet_2026-05-31.md`

Then inspect the current state and latest packet evidence:

- `src/rtdsl/v2_5_internal_readiness.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_execution_path_policy.py`
- `src/rtdsl/v2_5_determinism_policy.py`
- `docs/reports/goal2865_current_head_packet_after_front_doors_2026-05-31.md`
- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2855_summary.json`
- `docs/reports/goal2867_v2_5_app_facing_front_door_bypass_audit_2026-05-31.md`

## Main Work Bands To Audit

1. **Claude Review Intake And Goal Ordering**

   Key files:

   - `docs/reports/goal2773_claude_review_intake_and_revised_v2_5_plan_2026-05-31.md`
   - `docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md`
   - `docs/reports/goal2775_hit_stream_neutral_seam_reconciliation_2026-05-31.md`

   Questions:

   - Did the work actually respond to Claude's four main corrections: early
     neutral-buffer audit, partner-set mismatch, deterministic reduction bars,
     and tier-label drift?
   - Did it avoid building too much app-facing work on top of a stale
     torch-coercion seam?

2. **Generic Continuation And Adapter Surface**

   Key files:

   - `docs/reports/goal2776_v2_5_grouped_argmax_witness_reduction_2026-05-31.md`
   - `docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md`
   - `docs/reports/goal2778_v2_5_grouped_vector_sum_2026-05-31.md`
   - `docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md`
   - `docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md`
   - `docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md`
   - `docs/reports/goal2861_v2_5_generic_partner_front_door_completion_2026-05-31.md`
   - `docs/reports/goal2862_goal2861_generic_front_door_completion_consensus_2026-05-31.md`

   Questions:

   - Are the new public front doors generic and app-agnostic?
   - Is `v2_5_triton_front_door_coverage()` honestly describing API coverage,
     not speedup/release readiness?
   - Are deterministic tie-breaks, overflow behavior, and preview-not-promoted
     statuses preserved?

3. **Partner Selection, Determinism, And Tier Policy**

   Key files:

   - `docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md`
   - `docs/reports/goal2783_v2_5_app_migration_selection_guidance_2026-05-31.md`
   - `docs/reports/goal2791_thresholded_partner_selection_guidance_2026-05-31.md`
   - `docs/reports/goal2792_partner_selection_explain_plan_2026-05-31.md`
   - `docs/reports/goal2793_v2_5_partner_role_reconciliation_2026-05-31.md`
   - `docs/reports/goal2794_v2_5_continuation_determinism_policy_2026-05-31.md`
   - `docs/reports/goal2795_v2_5_tier_label_reconciliation_2026-05-31.md`
   - `docs/reports/goal2843_v2_5_execution_path_policy_2026-05-31.md`

   Questions:

   - Does the policy correctly say "primitive-first when the native fused path
     wins" and "partner path only when it wins under same-contract evidence"?
   - Does the code still block blind Triton auto-selection where Torch/CuPy or
     primitive-first paths are faster?
   - Are Tier A/B/C distinctions internally consistent?

4. **Canonical Benchmark Harnesses And Current Packet Evidence**

   Key files:

   - `docs/reports/goal2797_triangle_counting_v2_5_canonical_harness_2026-05-31.md`
   - `docs/reports/goal2798_librts_v2_5_warm_median_harness_2026-05-31.md`
   - `docs/reports/goal2799_spatial_rayjoin_v2_5_prepared_count_harness_2026-05-31.md`
   - `docs/reports/goal2800_rtnn_v2_5_live_ranked_summary_harness_2026-05-31.md`
   - `docs/reports/goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_2026-05-31.md`
   - `docs/reports/goal2802_rt_dbscan_v2_5_live_grouped_stream_harness_2026-05-31.md`
   - `docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md`
   - `docs/reports/goal2855_v2_5_current_canonical_harness_packet_runner_2026-05-31.md`
   - `docs/reports/goal2859_packet_runner_compact_child_output_2026-05-31.md`
   - `docs/reports/goal2865_current_head_packet_after_front_doors_2026-05-31.md`

   Questions:

   - Does the Goal2865 packet prove 7/7 current-head canonical harnesses pass
     at commit `3c5efc3130829aced34abb34f5863d3f3b652ad5`?
   - Are source-clean and claim-boundary checks sufficient?
   - Are compact child-output and progress logging safe and useful rather than
     hiding important failures?

5. **RTNN Campaign And Same-Stream / Batch Work**

   Key files:

   - `docs/reports/goal2810_rtnn_ranked_summary_aggregate_2026-05-31.md`
   - `docs/reports/goal2811_rtnn_density_aware_direct_aggregate_2026-05-31.md`
   - `docs/reports/goal2812_rtnn_prepared_query_aggregate_2026-05-31.md`
   - `docs/reports/goal2818_rtnn_campaign_checkpoint_2026-05-31.md`
   - `docs/reports/goal2821_rtnn_heterogeneous_batched_aggregate_requests_2026-05-31.md`
   - `docs/reports/goal2822_rtnn_fused_batch_block_partial_kernel_2026-05-31.md`
   - `docs/reports/goal2823_device_side_partial_reduce_negative_probe_2026-05-31.md`
   - `docs/reports/goal2824_rtnn_batch_chain_consensus_2026-05-31.md`
   - `docs/reports/goal2825_rtnn_cuda_graph_replay_prepared_batch_2026-05-31.md`
   - `docs/reports/goal2839_rtnn_same_stream_runner_mode_2026-05-31.md`
   - `docs/reports/goal2841_rtnn_same_stream_scale_probe_2026-05-31.md`

   Questions:

   - Are the RTNN performance conclusions honest and distribution-specific?
   - Were negative probes such as device-side partial reduction handled
     correctly and not buried?
   - Does the same-stream / CUDA graph direction remain generic enough for
     v2.5 and not drift into an RTNN-only engine path?

6. **Readiness Packet, Review Consensus, And Remaining Blocks**

   Key files:

   - `docs/reports/goal2806_v2_5_internal_readiness_packet_2026-05-31.md`
   - `docs/reports/goal2845_v2_5_internal_readiness_refresh_2026-05-31.md`
   - `docs/reports/goal2849_v2_5_readiness_indexes_current_canonical_harness_2026-05-31.md`
   - `docs/reports/goal2853_v2_5_readiness_next_actions_refresh_2026-05-31.md`
   - `docs/reports/goal2857_v2_5_readiness_indexes_packet_runner_2026-05-31.md`
   - `docs/reports/goal2863_v2_5_readiness_indexes_front_doors_2026-05-31.md`
   - `docs/reports/goal2864_goal2863_readiness_front_door_index_consensus_2026-05-31.md`
   - `docs/reports/goal2866_goal2865_current_head_packet_consensus_2026-05-31.md`
   - `docs/reports/goal2867_v2_5_app_facing_front_door_bypass_audit_2026-05-31.md`

   Questions:

   - Does `validate_v2_5_internal_readiness_packet()` accept for internal
     engineering readiness while still blocking release?
   - Are the blocked actions correct: release, public speedup, broad RT-core,
     whole-app speedup, true zero-copy, package-install, Triton preview
     auto-selection, and native app-specific engine logic?
   - Is there any stale review, stale report path, or mismatched consensus rule?

## Required Reviewer Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please include:

- findings first, ordered by severity;
- a verdict;
- explicit release-boundary statement;
- any required fixes before a future v2.5 release review;
- any optional future-work suggestions, clearly separated from blockers.

## Redlines

Do not authorize:

- v2.5 release;
- release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- automatic Triton preview selection;
- app-specific native engine logic.

If the evidence supports it, the strongest acceptable conclusion is:

> The last-day v2.5 internal engineering packet is coherent and accepted with
> boundaries; final release remains blocked pending an explicit user-requested
> release packet and fresh 3-AI release consensus.

## One-Sentence Pasteable Message

Please read `docs/handoff/CALL_FOR_REVIEW_GOAL2868_V2_5_LAST_DAY_WORK_SINCE_CLAUDE_REVIEWS_2026-05-31.md` and write a critical external review to `docs/reviews/goal2868_<reviewer>_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md`, auditing the v2.5 work from `3f8b1d5b` through `fbe28476` for correctness, app-agnostic boundaries, partner-selection honesty, current-head packet evidence, readiness gating, and remaining release blockers using one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
