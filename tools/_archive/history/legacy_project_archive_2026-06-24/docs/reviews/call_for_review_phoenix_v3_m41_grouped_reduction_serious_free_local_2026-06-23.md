# Call For Review: Phoenix V3 M41 Grouped-Reduction Serious Free Local Result

Requested reviewer: external AI reviewer

Requested verdict labels:

- `accept_contract_positive_paid_pod_blocked`
- `accept_with_caveats_try_larger_or_different_shape`
- `authorize_paid_pod_request`
- `block_m41_grouped_reduction_direction`

## Context

Claude reviewed the small M41 local CUDA smoke with verdict
`accept_with_caveats_before_paid_pod` and required a serious-scale free local
run before any paid POD request.

Codex ran that serious-scale free local run on `192.168.1.20`.

Review:

- `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_local_cuda_smoke_recorded_review_2026-06-23.md`
- `docs/reports/phoenix_v3_m41_grouped_reduction_serious_free_local_intake_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_serious_after_warmupfix_20260623_150500/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_serious_after_warmupfix_20260623_150500/productized_prepared_execution_runner.json`

## Result To Review

- row count: `262144`
- group count: `1024`
- repeat: `5`
- failed checks: `0`
- `step2_local_runner_contract_candidate`: `true`
- runner vs legacy hot: `3.456135x`
- runner vs legacy wall: `52.823894x`
- runner vs CPU hot: `0.498000x`
- Numba warning: low occupancy, grid size `4`

## Questions

1. Does this close the serious-scale local gate as contract-positive?
2. Does runner-vs-CPU hot `0.498x` block paid POD for grouped reduction?
3. Is a different grouped-reduction shape justified before abandoning this
   family for Step 2 performance evidence?
4. Should M41 close as "contract-positive, performance-blocked", or continue?
5. If continuing, what exact next local experiment is justified and bounded?
6. Are any claim boundaries too loose?
7. What P0/P1 work remains?

## Non-Authorization

This review request does not authorize release, all-app POD spend, paid focused
POD spend, public speedup wording, V4/embedding/C-ABI work, true-zero-copy
claims, or broad V3-over-V2 claims.
