# Goal3017: Numba Grouped Witness No-Host-Sync Fast Path

## Purpose

Goal3017 removes two avoidable host synchronizations from generated Numba
score-row witness paths:

- whole-score-column host copy for NaN validation;
- present-group host compaction through `counts.copy_to_host()`.

The conservative defaults remain unchanged. The fast path is only enabled when
the caller explicitly passes:

- `numba_known_dense_groups=True`;
- `numba_validate_group_ids=False`;
- `numba_validate_nan_scores=False`.

## Why This Is Safe for the Hausdorff Numba Modes

The two Hausdorff Numba modes use RTDL-owned Numba producer kernels:

- `pairwise_l2_sq_score_rows_2d`;
- `pairwise_l2_sq_block_nearest_rows_2d`.

Those producers structurally generate dense source-index group ids and finite
squared-L2 scores from caller point coordinates. The app therefore records the
fast-path status explicitly in each directed payload:

- `numba_known_dense_groups: True`;
- `host_present_group_compaction_used: False`;
- `nan_validation_host_sync_used: False`.

## Boundary

This does not authorize true zero-copy, release, speedup, RT-core speedup, or
whole-app speedup wording. It is an internal Numba partner-continuation
optimization and correctness-preserving fast option.

The option must not be used for arbitrary user-provided score rows unless the
caller can prove group density, group id validity, and score validity.
