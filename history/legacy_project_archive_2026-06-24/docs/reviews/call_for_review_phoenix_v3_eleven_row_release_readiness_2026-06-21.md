# Call For Review: Phoenix V3 Eleven-Row Release Readiness

Date: 2026-06-21

Reviewer: Claude external review requested from local Windows Claude Code.

## Review Task

Please perform a critical release-readiness review of the current Phoenix V3
state. The prior release-readiness consensus reviewed a six-row surface. The
current state is materially different: the Phoenix generic-engine active queue
is closed, the current M7 packet records eleven exact row-scoped M7-qualified
rows, and Spatial RayJoin has been closed out of current V3 as future research.

Use one verdict:

- `release-ready-with-scoped-wording`
- `not-release-ready-fix-p0`
- `not-release-ready-scope-as-preview`
- `reject-release`

## Questions To Answer

1. Does the current eleven-row M7 packet, with the active generic-engine queue
   closed, supersede the prior six-row release-readiness blocker?
2. If not, what exact P0 blockers remain before any V3 major release?
3. Can V3 be responsibly positioned as a narrow source-tree/pod-gated,
   row-scoped performance release, without claiming broad V3-over-V2 speedup?
4. Are the remaining blockers mainly engineering blockers, release packaging
   blockers, secondary-hardware evidence blockers, public-doc wording blockers,
   or product-positioning blockers?
5. What concrete improvement sequence should Codex do next?

## Current State Claims To Audit

- V3, not V4. C ABI, embedding, and external zero-copy interop are out.
- Release authorized: `false`.
- Broad V3-over-V2 speedup claim authorized: `false`.
- Current M7-qualified row-scoped count: `11`.
- Active generic-engine queue: empty.
- Current queue status:
  `generic_engine_work_queue_closed_not_release`.
- Current release readiness status:
  `blocked_not_release`.
- Current release blockers:
  - `release_authorization_false`
  - `eleven_row_surface_still_too_narrow_for_major_release`
  - `broad_v3_faster_than_v2_claim_not_authorized`
  - `general_release_installer_not_ready`
  - `secondary_rt_performance_confirmation_not_closed`
  - `external_release_readiness_consensus_blocks_major_release_wording`

## Current M7 Rows

The current release-readiness gate reports these eleven exact row-scoped M7
rows:

1. `grouped_reduction_sum_scalar_broadcast_repeat100_262144`
2. `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`
3. `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`
4. `aabb_candidate_stream_all_count_only_float32_32768`
5. `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50`
6. `aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50`
7. `rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02`
8. `component_union_clustered3d_65536_524288_repeat5_row_scoped`
9. `prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream`
10. `hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped`
11. `collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped`

## Files To Read

Please read these files before writing the review:

- `docs/reports/phoenix_v3_status_and_next_steps_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md`
- `docs/rebuild/v3/v3_claim_grade_all_benchmark_results_2026-06-20.md`
- `docs/rebuild/v3/v3_negative_route_explanations_2026-06-20.md`
- `docs/reviews/codex_phoenix_v3_six_row_release_readiness_2ai_consensus_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_spatial_active_p0_closure_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_spatial_active_p0_closure_2ai_consensus_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_rtnn_prepared_repeat50_amortization_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_rtnn_prepared_repeat50_amortization_2ai_consensus_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md`

## Output File

Write your review to:

`docs/reviews/claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md`

## Required Review Structure

Use this structure:

```text
# Claude Review: Phoenix V3 Eleven-Row Release Readiness

Verdict: <one verdict>

## Bottom Line

## Findings

## Answers To The Five Questions

## P0 Blockers

## P1/P2 Improvements

## Suggested Next Sequence

## Claim Boundary Check

## Evidence Gaps Or Weak Sources
```

Please be critical. Do not approve release just because tests pass. Do not
penalize V3 for intentionally excluding V4/C ABI/embedding. Treat broad
V3-over-V2 speedup as unauthorized unless the same-row evidence supports it.
