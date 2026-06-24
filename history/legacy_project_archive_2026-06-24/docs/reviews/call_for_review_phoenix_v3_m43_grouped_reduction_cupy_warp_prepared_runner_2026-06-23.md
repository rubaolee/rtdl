# Call For Review: Phoenix V3 M43 Grouped Reduction CuPy Warp Prepared Runner

Date: 2026-06-23

Requested verdict labels:

- `accept_m43_original_shape_hot_gate_cleared_continue_step2`
- `accept_m43_hot_gate_cleared_but_require_wall_followup`
- `revise_m43_contract_or_metadata`
- `reject_m43_not_generic_runtime_work`

Please review:

- `docs/reports/phoenix_v3_m43_grouped_reduction_cupy_warp_prepared_runner_2026-06-23.md`
- `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_original_262144x1024_20260623_153707/summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m43_lx1_cupy_warp_trust_offsets_262144x1024_20260623_154342/summary.json`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/prepared_execution.py`
- `src/rtdsl/numba_partner_continuation.py`
- `scripts/v3_phoenix_grouped_reduction_m41_local_harness.py`

Review questions:

1. Is M43 generic runtime work rather than app-specific tuning?
2. Does the CuPy prepared-session route preserve explicit partner choice and claim boundaries?
3. Does the original blocked shape (`262144 x 1024`) now clear the CPU-hot inversion gate?
4. Does the trusted-offset follow-up fairly identify the runner-vs-legacy-wall regression as row-offset validation overhead, and is explicit `--trust-row-offsets` acceptable as a prevalidated-data mode?
5. Are launch metadata fields sufficient for future review (`partner`, `kernel_strategy`, `program_count`, `groups_per_block`, `threads_per_group`, residency flags)?
6. Does the report correctly avoid release, all-app, paid POD, public speedup, broad V3-over-V2, V4, embedding, C ABI, and true-zero-copy authorization?
7. What exact next step is authorized: Step-2 grouped-reduction closure, local wall-followup, another family, or no-go?

Non-authorization to preserve:

- no release
- no all-app
- no paid POD
- no public speedup wording
- no broad V3-over-V2 claim
- no V4
- no embedding
- no C ABI
- no true-zero-copy claim
