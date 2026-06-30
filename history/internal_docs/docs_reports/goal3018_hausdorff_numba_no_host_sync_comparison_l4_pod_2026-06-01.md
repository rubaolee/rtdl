# Goal3018: Hausdorff Numba No-Host-Sync Comparison

## Purpose

Goal3018 records the L4 pod comparison after Goal3017 removed avoidable host
synchronization from generated Numba score-row witness paths.

The compared modes are:

- `partner_numba_witness_exact`: dense device-generated score rows;
- `partner_numba_block_nearest_exact`: bounded tile-nearest summary rows.

## Evidence

Artifact:

`docs/reports/goal3018_hausdorff_numba_no_host_sync_comparison_l4_pod_2026-06-01.json`

Collected from clean commit:

`4c9f947814662ebfc4575710f274b523f5617b58`

on:

`NVIDIA L4, 565.57.01`

The evidence run used `copies=512`, producing `2048 x 2048` points per
directed pass.

| Mode | Logical Pairs | Materialized Summary Rows | Wall Seconds | Notes |
| --- | ---: | ---: | ---: | --- |
| `partner_numba_witness_exact` | 4,194,304 | 4,194,304 | 0.7739660553634167 | dense device score rows |
| `partner_numba_block_nearest_exact` | 4,194,304 | 16,384 | 1.0773870013654232 | bounded tile summaries |

The internal `block_vs_dense_wall_ratio` is `1.3920339191872373`, so the dense
device-score path is the current faster Numba Hausdorff path at this scale.
The block-nearest path is still useful as a memory-pressure and future
streaming-design path because it reduces materialized rows by 256x.

Conclusion: dense device-score path is the current faster Numba Hausdorff path.

## Boundary

This is internal phase-timing evidence only. It does not authorize v2.6 release,
public speedup wording, Numba speedup wording, RT-core speedup wording,
whole-app speedup wording, true-zero-copy wording, or app-specific native-engine
logic.

Both modes are exact Numba partner paths and do not call native RT traversal.
