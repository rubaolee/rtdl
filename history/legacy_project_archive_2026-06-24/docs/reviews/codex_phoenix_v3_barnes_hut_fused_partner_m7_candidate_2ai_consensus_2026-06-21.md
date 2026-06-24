# Codex Consensus: Phoenix V3 Barnes-Hut Fused Partner M7 Candidate

Status: `claude_codex_consensus_complete_approve_one_row_scoped_m7_with_amendments`.

External review:
`docs/reviews/claude_phoenix_v3_barnes_hut_fused_partner_m7_candidate_review_2026-06-21.md`

Candidate packet:
`docs/rebuild/v3/phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md`

Consensus:

Codex accepts Claude's `approve-with-amendments` verdict for exactly one
Phoenix V3 M7 milestone row:

`aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped`

Allowed row-scoped capability:

Generic aggregate-tree fused weighted-vector sum, Numba CUDA partner
(`generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1`): at
131,072 bodies on a Barnes-Hut tree (theta=0.5, 2D), 45.493 ms wall-repeat
median (r=11, warmup=3), 4.082x faster than CPU/Numba fused baseline. Not an
RT-core claim. Large-scale validation: route parity plus checksum across three
scales; independent exact-force CPU oracle is not claimed at this scale.

Required amendments applied to the row record:

- `evidence_tree_structure: barnes_hut_theta_0.5_2d_bucketized`
- `large_scale_validation_tier: route_parity_plus_checksum_no_independent_oracle`
- Primary wording uses the 4.082x CPU/Numba fused comparison.
- The 13.591x comparison against the current prepared RTDL/OptiX
  frontier-emission route is retained only as supporting metadata because that
  OptiX route is already no-go.
- The row pins the source artifact:
  `docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json`.

Explicit non-approvals:

- No V3 release authorization.
- No whole-application Barnes-Hut claim.
- No RT-core acceleration claim.
- No broad V3-over-V2 claim.
- No paper reproduction claim.
- No public release row until an independent exact-force CPU oracle at scale
  and separate release review exist.

Goal-level decision audit:

1. Was I foolish? No. Claude approved only a narrow amended M7 milestone row,
   and this consensus keeps release/public/broad/RT-core flags false.
2. If yes, what actions made the decision foolish? The foolish action would
   have been to headline `13.591x over OptiX` even though that OptiX route is
   no-go, or to treat this as release readiness.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: leave aggregate_frontier missing until a native RT route exists. That
   is stricter but discards reviewed V3 partner evidence that matches the
   explicit-partner contract.
4. Can I now try a different path that actually solves the problem? Yes: add
   exactly one amended M7 row to close the aggregate_frontier breadth gap while
   leaving Spatial topology-stream and release readiness blocked.
