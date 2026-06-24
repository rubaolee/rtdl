# Codex 2-AI Consensus: Phoenix V3 Twelve-Row Release Readiness After P1 Fixes

Status: `twelve_row_release_readiness_consensus_blocks_release`.

Date: 2026-06-21.

This consensus combines:

- Claude external review:
  `docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_after_p1_fixes_compact_review_2026-06-21.md`
- Prior Claude review:
  `docs/reviews/claude_phoenix_v3_twelve_row_release_readiness_review_2026-06-21.md`
- Current release gate:
  `docs/rebuild/v3/phoenix_v3_release_readiness_gate_2026-06-21.json`
- Current final wording gate:
  `scripts/v3_release_wording_gate.py`
- Current test matrix result:
  `scripts/run_test_matrix.py --group v3_rebuild` passed with 96 modules / 463
  tests OK.

## Verdict

V3 is not release-ready.

```text
twelve_row_release_readiness_consensus_blocks_release
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

The current 12 row-scoped M7 rows are real scoped evidence, but they are not
enough for a responsible major V3 release.

## P1 Fix Closure

Claude confirmed P1-4 is fully fixed: the wording gate now scans naked
`13.591x` Barnes-Hut wording and only allows it when the surrounding context
marks it as supporting no-go metadata, not a primary claim.

Claude confirmed P1-1 is mechanically fixed and required this consensus to
resolve the installer-scope carry-over. Codex resolves it here:

```text
source_tree_pod_gated_twelve_row is accepted as the correct successor to
source_tree_pod_gated_eleven_row for the current blocked V3 rebuild scope.
installer_closes_release_blocker: true
installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row
general_release_installer_ready: false
package_install_claim_authorized: false
release_authorized: false
```

Reason: the twelfth row,
`aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped`,
uses the same RTX 4000 Ada pod class and the same staged GPU Python package
family as the prior source-tree/pod-gated rows. This closes only the scoped
source-tree/pod-gated installer blocker. It does not create a general package
installer, PyPI install claim, multi-GPU claim, or release authorization.

## Current Blocking Reasons

The following blockers remain valid under twelve-row scope:

```text
release_authorization_false
twelve_row_surface_still_too_narrow_for_major_release
missing_point_location_topology_stream_m7_capability_family
twelve_row_release_readiness_consensus_blocks_release
```

The consensus blocker now replaces the temporary
`twelve_row_release_readiness_consensus_missing` label. The consensus exists,
and it blocks release.

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

Barnes-Hut remains a generic aggregate-tree fused weighted-vector Numba CUDA
partner row. It opens no RT-core claim, no whole-app claim, no automatic backend
selection claim, and no broad V3-over-V2 claim. The `13.591x` value is only a
supporting no-go comparison against the current prepared RTDL/OptiX
frontier-emission route.

## Carryover P1 Items

These items do not block this consensus, but they block any future release
authorization attempt:

- external review acceptance for app catalog, backend maturity, and performance
  model;
- reviewer acceptance that tutorials 07-15 are coherent for release review;
- final placement and reviewer acceptance of negative-row wording for the
  0.065x and 0.034x historical route-health rows.

## Decision

Do not publish V3.

Continue Phoenix V3 only through the remaining major-release blockers:

- create or reject a real `point_location_topology_stream` M7 row;
- if the surface remains 8 of 9, make an explicit product-scope decision rather
  than pretending the gap is closed;
- keep all public docs and tutorials scoped to the exact 12 rows until the
  missing family is resolved.

## Goal-Level Decision Self-Audit

Decision: accept Claude's post-fix review and write the Codex twelve-row
release-readiness consensus as blocked-not-release.

1. Was I foolish? No. The consensus follows a fresh external review, current
   gates, and a full v3_rebuild matrix.
2. If yes, what actions made it foolish? The foolish action would be to treat
   this consensus as release permission, or to leave the consensus blocker as
   missing after writing the consensus.
3. Was there another path? Yes. Codex could demand a fresh scoped installer
   review before consensus. Claude allowed resolving that P1 inside this
   consensus because all release flags remain false and the twelfth row uses the
   same source-tree/pod-gated GPU package family.
4. Can I now try a different path? Yes. Replace the temporary missing-consensus
   blocker with this explicit blocks-release consensus, then keep V3 work aimed
   at the missing `point_location_topology_stream` family or an explicit scope
   decision.
