# Goal1651 v1.6.x OptiX Collect-K Fused Materialize-Mark Probe

## Verdict

`fused_materialize_mark_candidate_rejected`

This records a rejected opt-in diagnostic path for `COLLECT_K_BOUNDED` merge levels:

`RTDL_OPTIX_COLLECT_K_FUSED_MATERIALIZE_MARK_DIAGNOSTIC=1`

The tested path used the existing fused `collect_k_bounded_i64_row_width2_final_materialize_mark_counts_level_counts` kernel for device-count derived levels. It was not enabled by `RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE`, and the candidate code is not retained after the negative result.

## Rationale

After Goal1650, the `262144` fastest path is valid and sub-millisecond on the A4500 pod, but merge work still dominates:

- `total_ms=0.677170`
- `merge_launch_ms=0.164855`
- `merge_sync_ms=0.322180`
- `merge_launches=27`

The fused diagnostic tries to reduce per-level launch work by replacing separate materialize and mark-count kernels with a fused kernel. Because the fused kernel only writes marks for valid outputs and uses atomic block counts, the diagnostic explicitly clears `final_marks` and `final_block_counts` before the fused launch.

## Result

On the A4500 pod at commit `764e92819fd9ad7e20f2dde12ce0dfa5f081f2b0` plus the local diagnostic patch:

- Baseline fastest `candidate_count=262144`: `total_ms=0.677170`, `merge_sync_ms=0.322180`.
- Fused diagnostic `candidate_count=262144`: `total_ms=1.042890`, `merge_sync_ms=0.661559`.
- Parity remained accepted, but performance regressed.

Artifacts:

- `docs/reports/goal1651_fused_262144.json`
- `docs/reports/goal1651_fused_262144.jsonl`
- `docs/reports/goal1651_fused_262144.md`

## Decision

`do_not_promote`

The fused materialize-mark candidate is rejected. The added atomics and memset work cost more than the launch reduction.

## Claim Boundary

This file records a rejected diagnostic candidate only. It does not authorize public speedup wording, stable `COLLECT_K_BOUNDED` promotion, fastest-candidate promotion, release tags, or release action.
