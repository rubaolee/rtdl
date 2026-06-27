# Claude Recorded Review: Phoenix V3 M41 Grouped-Reduction Local Harness

Date: 2026-06-23
Raw review:
`docs/reviews/claude_phoenix_v3_m41_grouped_reduction_second_family_local_harness_review_2026-06-23.raw.md`

Verdict: `accept_with_caveats_before_cuda_smoke`

## Meaning

Claude accepted the M41 family selection and generic harness shape, but blocked
advancement until a real CUDA smoke exists and P1 harness issues are fixed.

Accepted:

- grouped reduction is the right second local family after component-union;
- CPU / legacy one-shot / productized-runner structure is sufficient;
- harness is generic and app-agnostic;
- hot and wall metrics are the right structure;
- claim boundaries are strict.

Not accepted as complete:

- no real CUDA execution existed in the packet at review time;
- signature correctness relied too much on strict hash equality;
- adapter row/group count verification was implicit rather than explicit.

## Required Fixes

P0: run a real local CUDA smoke before any paid POD request.

P1.1: add numeric tolerance/allclose correctness alongside hash comparison.

Applied:

- `comparison_payload()` now emits
  `all_variant_vector_sum_signatures_allclose`;
- failure checks use allclose rather than strict hash equality;
- strict hash remains visible as
  `all_variant_vector_sum_signatures_hash_match`.

P1.2: explicitly expose adapter row/group counts from the productized runner.

Applied:

- `run_grouped_vector_sum_2d_prepared_session` now reports
  `adapter_row_count`, `adapter_group_count`, and `adapter_counts_present`;
- the M41 harness emits `adapter_contract_verification`;
- tests assert these fields.

P2.1: clarify same-row guarantee.

Applied:

- M41 harness emits `same_rows_per_process=true`.

P2.2: enumerate embedding and C-ABI prohibitions.

Applied:

- M41 harness emits `embedding_work_authorized=false`;
- M41 harness emits `c_abi_work_authorized=false`.

P2.3: warmup count 1 is marginal.

Applied:

- M41 default warmup is now `2`.

## Post-Review Validation

Focused validation after fixes:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_m41_grouped_reduction_harness_test tests.v3_release_wording_gate_test
Ran 9 tests
OK
```

Full `v3_rebuild` after smoke-related fixes:

```text
module_count: 120
Ran 626 tests in 77.136s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m41_cuda_smoke_fixes_20260623_145328.stdout.txt
```

Free local CUDA smoke after fixes:

- host: `192.168.1.20` / `lx1`
- GPU: `NVIDIA GeForce GTX 1070`
- artifact:
  `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_smoke_after_hotfix_20260623_145500/`
- status: `grouped_reduction_m41_local_run_complete_not_release`
- failed checks: `0`
- `step2_local_runner_contract_candidate`: `true`
- `all_variant_vector_sum_signatures_allclose`: `true`
- `all_variant_vector_sum_signatures_hash_match`: `false`
- `runner_vs_legacy_hot_speedup`: `4.284241304411924x`
- `runner_vs_legacy_wall_speedup`: `66.0341234055151x`

Important boundary: this was a small non-serious local CUDA smoke with a Numba
low-occupancy warning. It is not paid POD evidence and not a public performance
claim.

## Non-Authorization Block

This recorded review does not authorize release, all-app POD spend, paid focused
POD spend, public speedup wording, V4/embedding/C-ABI work, true-zero-copy
claims, or broad V3-over-V2 claims.
