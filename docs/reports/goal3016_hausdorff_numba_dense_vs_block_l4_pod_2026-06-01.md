# Goal3016: Hausdorff Numba Dense-vs-Block Pod Comparison

## Purpose

Goal3016 compares two exact Numba Hausdorff partner modes in one warmed pod
process:

- `partner_numba_witness_exact`: device-generated dense pairwise score rows;
- `partner_numba_block_nearest_exact`: bounded per-source/tile nearest rows.

The runner is:

`scripts/goal3016_hausdorff_numba_mode_comparison_pod_runner.py`

## Boundary

This comparison is internal phase-timing evidence only. It does not authorize
v2.6 release, public speedup wording, Numba speedup wording, RT-core speedup
wording, whole-app speedup wording, true-zero-copy wording, or app-specific
native-engine logic.

Both modes are exact partner paths and do not call native RT traversal.

Blocked wording includes `RT-core speedup wording`.

## Expected Artifact

After pod execution, the expected artifact is:

`docs/reports/goal3016_hausdorff_numba_dense_vs_block_l4_pod_2026-06-01.json`

The artifact must record clean source status, GPU/driver, warmup summaries,
evidence summaries, oracle parity, claim-boundary flags, and the internal
`block_vs_dense_wall_ratio`.
