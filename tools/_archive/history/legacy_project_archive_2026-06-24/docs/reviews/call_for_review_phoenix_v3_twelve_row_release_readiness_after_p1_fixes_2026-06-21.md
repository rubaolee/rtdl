# Call For Review: Phoenix V3 Twelve-Row Release Readiness After P1 Fixes

Status: request for external critical review.

Please review the current Phoenix V3 state after the P1 fixes from the previous
twelve-row release-readiness review.

## Current Facts

- Current M7 row-scoped release rows: 12.
- Current M7 capability-family coverage: 8 of 9.
- Missing M7 capability family: `point_location_topology_stream`.
- Release gate status: `blocked_not_release`.
- Release remains unauthorized.
- Public speedup claim remains unauthorized.
- Broad V3-over-V2 claim remains unauthorized.
- Current install scope: `source_tree_pod_gated_twelve_row`.
- Full local gate/matrix result after fixes: `scripts/run_test_matrix.py --group v3_rebuild`
  passed, 96 modules / 463 tests OK.

## P1 Fixes Since Prior Claude Review

The previous Claude review was saved at:

`docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_review_2026-06-21.md`

It returned `approve-blocked-not-release` and called out these relevant fixes:

- P1-1: update install gate scope from `source_tree_pod_gated_eleven_row` to
  twelve-row.
- P1-4: add an overclaim scanner for naked `13.591x` Barnes-Hut wording.

Those fixes are now in place:

- `scripts/v3_phoenix_install_reproducibility_gate.py`
- `tests/v3_phoenix_install_reproducibility_gate_test.py`
- `scripts/v3_phoenix_release_readiness_gate.py`
- `tests/v3_phoenix_release_readiness_gate_test.py`
- `scripts/v3_release_wording_gate.py`
- `tests/v3_release_wording_gate_test.py`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/rebuild/v3/v3_install_reproducibility_strategy_2026-06-21.md`
- `docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md`
- `docs/rebuild/v3/v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md`

The wording gate now passes with all 12 expected row IDs and no violations.
The install/reproducibility gate now reports:

```text
release_scope: source_tree_pod_gated_twelve_row
installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row
general_release_installer_ready: false
release_authorized: false
```

The release-readiness gate now reports:

```text
status: blocked_not_release
blocking_reasons:
- release_authorization_false
- twelve_row_surface_still_too_narrow_for_major_release
- missing_point_location_topology_stream_m7_capability_family
- twelve_row_release_readiness_consensus_missing
```

## Twelve Current Row-Scoped M7 Rows

```text
grouped_reduction_sum_scalar_broadcast_repeat100_262144
grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups
grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups
aabb_candidate_stream_all_count_only_float32_32768
aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50
aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50
rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02
component_union_clustered3d_65536_524288_repeat5_row_scoped
prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream
hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped
collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped
aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped
```

## Files To Inspect

Primary current gates and docs:

- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_install_reproducibility_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_secondary_platform_gate_2026-06-21.json`
- `docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.json`

Barnes-Hut P1-4 boundary:

- `docs/rebuild/v3/phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md`
- `docs/reviews/claude_phoenix_v3_barnes_hut_fused_partner_m7_candidate_review_2026-06-21.md`
- `docs/reviews/codex_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2ai_consensus_2026-06-21.md`
- `scripts/v3_release_wording_gate.py`

## Review Questions

1. Are P1-1 and P1-4 actually fixed?
2. Is the current `blocked_not_release` gate honest and sufficient after the
   fixes?
3. Should a Codex two-AI consensus now record `twelve_row_release_readiness_consensus_blocks_release`
   rather than `twelve_row_release_readiness_consensus_missing`, assuming you
   agree release remains blocked?
4. Are there any remaining P0/P1 issues that would make the current status docs,
   gates, or tutorial surface misleading to users?
5. Give a verdict using one of:
   `approve-blocked-not-release`, `reject-missing-p0`, or
   `approve-release-ready`.

## Goal-Level Decision Self-Audit

Decision: request a fresh external review after the install-scope and wording
scanner fixes, before Codex writes a two-AI consensus.

1. Was I foolish? No. The previous external review required these fixes before
   a fresh aggregate decision.
2. If yes, what actions made it foolish? The foolish action would be to reuse
   the stale eleven-row consensus or old twelve-row review after the P1 fixes.
3. Was there another path? I could write Codex consensus without an external
   rerun, but that would violate the project review rule.
4. Can I now try a different path? Use the verified local Claude CLI by absolute
   path, save the review, and then write Codex consensus from the external
   result plus local gates.
