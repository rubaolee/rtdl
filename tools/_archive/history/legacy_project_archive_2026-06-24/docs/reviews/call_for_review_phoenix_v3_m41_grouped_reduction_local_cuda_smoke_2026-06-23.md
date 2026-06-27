# Call For Review: Phoenix V3 M41 Grouped-Reduction Local CUDA Smoke

Requested reviewer: external AI reviewer

Requested verdict labels:

- `accept_m41_local_cuda_smoke_continue_reviewed_step2`
- `accept_with_caveats_before_paid_pod`
- `block_m41_cuda_smoke_invalid`
- `block_m41_paid_pod`

## Context

Claude reviewed the M41 local harness with verdict
`accept_with_caveats_before_cuda_smoke`.

Codex applied the requested fixes:

- numeric allclose correctness gate alongside strict hash;
- explicit adapter row/group count fields;
- separate embedding/C-ABI prohibitions;
- `same_rows_per_process`;
- default warmup increased to `2`.

Focused tests after fixes ran 9 tests OK.

Then Codex ran the harness on the free local Linux CUDA machine, not paid POD.

Review these files:

- `docs/reviews/claude_phoenix_v3_m41_grouped_reduction_second_family_local_harness_recorded_review_2026-06-23.md`
- `docs/reports/phoenix_v3_m41_grouped_reduction_local_cuda_smoke_intake_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_smoke_after_hotfix_20260623_145500/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m41_lx1_smoke_after_hotfix_20260623_145500/productized_prepared_execution_runner.json`
- `scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`
- `tests/v3_phoenix_m41_grouped_reduction_harness_test.py`

## Result To Review

Local CUDA smoke:

- host: `192.168.1.20` / `lx1`
- GPU: `NVIDIA GeForce GTX 1070`
- row count: `8192`
- group count: `128`
- repeat: `5`
- status: `grouped_reduction_m41_local_run_complete_not_release`
- failed checks: `0`
- `step2_local_runner_contract_candidate`: `true`
- `all_variant_vector_sum_signatures_allclose`: `true`
- `all_variant_vector_sum_signatures_hash_match`: `false`
- `runtime_trunk_executes_end_to_end`: `true`
- `internal_device_residency_between_rtdl_phases`: `true`
- `hot_path_host_materialization`: `false`
- `adapter_row_count`: `8192`
- `adapter_group_count`: `128`

Computed comparisons:

- runner vs legacy hot: `4.284241x`
- runner vs legacy wall: `66.034123x`
- runner vs CPU hot: `0.043677x`

Boundary:

- this is a small local CUDA smoke only;
- low-occupancy warning was emitted;
- no paid POD or public performance claim is authorized by this packet.

## Questions

1. Does this close the M41 P0 "no real CUDA execution" finding?
2. Are P1.1 and P1.2 adequately fixed?
3. Is the smoke valid as a local execution/contract gate despite being small?
4. Does the CPU-hot result require additional wording before any future review?
5. Is a serious focused paid POD justified next, or should we first run a larger
   free local Linux smoke?
6. Are the claim boundaries still strict enough?
7. What P0/P1 work remains before M41 can be closed?

## Non-Authorization

This review request does not authorize release, all-app POD spend, paid focused
POD spend, public speedup wording, V4/embedding/C-ABI work, true-zero-copy
claims, or broad V3-over-V2 claims.
