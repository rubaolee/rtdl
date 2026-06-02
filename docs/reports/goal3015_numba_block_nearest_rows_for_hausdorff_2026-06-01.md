# Goal3015: Numba Block-Nearest Rows for Hausdorff

## Purpose

Goal3015 adds a bounded/streaming Numba score-row producer for point-pair
nearest-witness workloads:

`pairwise_l2_sq_block_nearest_rows_2d`

Instead of materializing every source-target score row, it emits one nearest
candidate row per source point and target tile. The Hausdorff app then runs the
same generic grouped witness reducer over those partial rows.

## New App Mode

The Hausdorff benchmark app now accepts:

`partner_numba_block_nearest_exact`

The mode composes:

1. `pairwise_l2_sq_block_nearest_rows_2d_partner_columns(..., partner="numba")`;
2. `group_argmin_then_global_argmax_partner_columns(..., partner="numba")`;
3. Python final undirected Hausdorff selection.

## Boundary

This is still a Numba partner path, not an RT-core path. It does not call native
RT traversal and does not add app-specific native-engine logic.

It deliberately records:

- `host_score_row_materialization_used: False`;
- `score_rows_generated_on_partner_device: True`;
- `bounded_tile_summary_rows: True`;
- `rt_core_accelerated: False`.

The operation is exact because every target point is covered by exactly one
tile, and the downstream grouped argmin chooses the best tile-level candidate
for each source point.

## Claim Boundary

Goal3015 does not authorize:

- v2.6 release;
- public speedup wording;
- Numba speedup wording;
- RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- automatic partner selection;
- app-specific native-engine logic.

## Next Step

Run the block-nearest mode on the L4 pod and compare it against the Goal3013
dense score-row evidence as phase-timing data only. Any public performance
claim still needs same-contract comparison and external review.
