# Phoenix V3 Barnes-Hut Fused Partner M7 Candidate

Status: `aggregate_tree_fused_partner_m7_candidate_pending_external_review`.

This packet does not promote a row. It prepares one narrow aggregate-frontier/vector-accumulation
candidate for external review after the same-basis no-go closed the current prepared OptiX
frontier-emission shape.

```text
candidate_row_id: aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped
contract: generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1
release_authorized: false
row_scoped_public_speedup_claim_authorized: false
rt_core_speedup_claim_authorized: false
m7_promotion_authorized: false
candidate_m7_contribution_if_external_review_approves: 1
```

## Large Same-Basis Rows

| Bodies | Candidate wall | CPU/Numba over candidate | Supporting no-go current OptiX frontier metadata | Contribution rows |
|---:|---:|---:|---:|---:|
| 32,768 | 11.739 ms | 7.492x | 7.022x | 15,514,679 |
| 65,536 | 35.643 ms | 3.102x | 4.990x | 55,935,606 |
| 131,072 | 45.493 ms | 4.082x | 13.591x | 68,023,506 |

## Draft Claim Under Review

For the generic aggregate-tree fused weighted-vector partner row at 131,072 bodies, the Numba CUDA partner route completed in 45.493 ms wall-repeat median, 4.082x faster than CPU/Numba fused. The 13.591x comparison against the current prepared RTDL/OptiX frontier-emission route is supporting no-go metadata only, not the primary claim. This is not an RT-core claim.

## Current Blockers

- external_ai_review_not_done_for_candidate_row
- large-row validation is route parity plus checksums; independent exact-force CPU oracle is not claimed
- candidate is a Numba CUDA partner route, not RT-core acceleration
- no whole-application Barnes-Hut, paper-reproduction, automatic-backend-selection, or broad V3-over-V2 claim

## Next Actions

- Send this candidate packet to external AI review.
- If external review approves, add exactly one row-scoped aggregate_frontier/vector_accumulation M7 row.
- Keep public speedup and release flags false until that reviewed classification packet lands.
- Do not rewrite current prepared OptiX frontier-emission no-go into a win.

## Goal-Level Decision Self-Audit

1. Was I foolish? No. I separated the slow RT frontier-emission no-go from the fast generic partner route.
2. If yes, what actions made it foolish? The foolish action would be to discard the whole aggregate family after the OptiX path failed, or to claim RT-core acceleration from a Numba CUDA partner result.
3. Was there another path? I could force a native OptiX redesign now, but the saved evidence shows the reusable partner route is the current performance path and fits V3's explicit-partner contract.
4. Can I now try a different path? Use external review to decide whether this one row-scoped partner capability can close the aggregate_frontier breadth gap, while keeping release and broad claims false.
