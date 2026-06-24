# Compact Call For Review: Phoenix V3 Twelve-Row Release Readiness After P1 Fixes

You are Claude Code. Return a critical release-readiness review in Markdown.
Do not edit files. Use the facts below as the reviewed evidence summary.

## Verified Current Facts

- Project: RTDL Phoenix V3 rebuild, V3-only.
- Full local matrix after fixes: `scripts/run_test_matrix.py --group v3_rebuild`
  passed, 96 modules / 463 tests OK.
- Wording gate: pass, all 12 expected row IDs present, no violations.
- Install/repro gate: pass under scoped release only:
  - `release_scope: source_tree_pod_gated_twelve_row`
  - `installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row`
  - `general_release_installer_ready: false`
  - `package_install_claim_authorized: false`
  - `release_authorized: false`
- Secondary platform gate: compatibility confirmed only under reviewed
  single-RTX hardware-scope waiver:
  - scope: `single_rtx_4000_ada_driver_550_127_05_pod`
  - `secondary_rt_performance_confirmation_authorized: false`
  - `multi_gpu_performance_portability_claim_authorized: false`
- Release readiness gate:
  - `status: blocked_not_release`
  - `m7_qualified_release_rows: 12`
  - `public_speedup_claim_authorized: false`
  - `broad_v3_faster_than_v2_claim_authorized: false`
  - `release_authorized: false`
  - blocking reasons:
    - `release_authorization_false`
    - `twelve_row_surface_still_too_narrow_for_major_release`
    - `missing_point_location_topology_stream_m7_capability_family`
    - `twelve_row_release_readiness_consensus_missing`
- M7 capability-family coverage: 8 of 9.
- Missing M7 capability family: `point_location_topology_stream`.
- Current next-engine queue has no active promotable old-evidence items; spatial
  topology-stream remains future work.

## P1 Fixes Completed From Your Previous Review

Prior review:
`docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_review_2026-06-21.md`

You previously returned `approve-blocked-not-release` and required:

- P1-1: update install gate scope from eleven-row to twelve-row.
- P1-4: add a scanner so naked `13.591x` Barnes-Hut wording is flagged unless
  it is clearly supporting no-go metadata, not a primary claim.

Current result:

- P1-1 fixed in install gate, release gate, runbook, status docs, and tests.
- P1-4 fixed in `scripts/v3_release_wording_gate.py` and tests.
- Current status docs were patched from 11-row to 12-row.
- Old aggregate gate JSON alias was regenerated from the current release gate.

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

Barnes-Hut boundary: the approved row is a generic aggregate-tree fused
weighted-vector Numba CUDA partner row. The allowed claim is 45.493 ms
wall-repeat median at 131,072 bodies, 4.082x faster than CPU/Numba fused. The
13.591x comparison against the current prepared RTDL/OptiX frontier-emission
route is supporting no-go metadata only, not a primary claim, and not an
RT-core claim.

## Questions

1. Are P1-1 and P1-4 fixed?
2. Is `blocked_not_release` still the correct release-readiness status?
3. Should Codex now write the 2-AI consensus as
   `twelve_row_release_readiness_consensus_blocks_release`, replacing the
   temporary `twelve_row_release_readiness_consensus_missing` blocker after the
   consensus file exists?
4. Are there any remaining P0/P1 issues in this compact evidence summary?
5. Verdict: choose exactly one of `approve-blocked-not-release`,
   `reject-missing-p0`, or `approve-release-ready`.

## Required Tone

Be critical. Do not reward the project for saying correct words if the facts do
not justify release.
