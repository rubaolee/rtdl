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

## Observed Artifact

The pod artifact is:

`docs/reports/goal3016_hausdorff_numba_dense_vs_block_l4_pod_2026-06-01.json`

It was collected from clean commit:

`dc4ab582f3c89e88eae596224d56a20cae0a428f`

on:

`NVIDIA L4, 565.57.01`

The evidence run used `copies=512`, producing `2048 x 2048` points per
directed pass.

| Mode | Logical Pairs | Materialized Summary Rows | Wall Seconds | Notes |
| --- | ---: | ---: | ---: | --- |
| `partner_numba_witness_exact` | 4,194,304 | 4,194,304 | 1.3491788320243359 | dense device score rows |
| `partner_numba_block_nearest_exact` | 4,194,304 | 16,384 | 1.4156021513044834 | bounded tile summaries |

The internal `block_vs_dense_wall_ratio` is `1.049232405448049`: the bounded
path greatly reduces row materialization, but it is not faster on this L4 run.
Treat it as a memory-pressure path and design signal, not as a recommended
performance path yet.
