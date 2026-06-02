# Goal3044 Hausdorff Grouped Witness Index Mapping Cleanup

Date: 2026-06-02

Status: source cleanup landed; pod smoke pending.

## Purpose

The Goal3043 Claude review accepted Goal3042 with boundary and identified one
pre-existing inconsistency: older grouped one-row reducers sometimes passed
`sorted_target_columns` into `_reduce_nearest_max_distance_row(...)`. The native
nearest-witness rows carry original point IDs, so the reducer should map those
IDs back through the original target column table. Passing the sorted table keeps
the distance correct but can report a target index in BVH-sort order.

Goal3044 fixes that witness-index reporting inconsistency.

## What Changed

In `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`,
the following app-level paths now pass original `target_columns` to
`_reduce_nearest_max_distance_row(...)`:

- `_directed_rt_grouped_reduced_nearest_witness`
- `_directed_rt_grouped_adaptive_reduced_nearest_witness`
- `_directed_rt_grouped_device_columns_numba_argmax_nearest_witness`

Goal3042's active-frontier path already used the original target columns after
the witness-index fix in commit `0f0c4bfd`.

## Boundary

This is an app-level Python cleanup. It does not alter native ABI, native engine
behavior, performance claims, release status, or true-zero-copy status. It only
makes returned `target_index` fields consistently refer to original input rows
when the underlying native row returns original point IDs.
