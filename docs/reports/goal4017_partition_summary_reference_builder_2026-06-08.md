# Goal4017 Partition Summary Reference Builder

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal4017 adds a small Python reference builder for the Goal4016 partition
convergence typed-stream contract. This gives the future native OptiX producer a
deterministic oracle for small inputs before performance work starts.

This does not add a native ABI, does not execute on RT cores, and does not
authorize public speedup wording.

## What Changed

Added:

- `build_v2_8_fixed_radius_partition_convergence_summary_reference_3d`
  in `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`;
- export through `rtdsl.__init__`;
- `tests/goal4017_partition_summary_reference_builder_test.py`.

The reference builder computes:

- `point_partition_ids`;
- `occupied_partition_keys_x/y/z`;
- `partition_offsets`;
- `partition_counts`;
- partition AABB columns;
- `near_pair_left_partition_ids`;
- `near_pair_right_partition_ids`;
- `near_pair_status`.

The `near_pair_status` values are generic:

- `0`: safe-skip partition pair;
- `1`: safe-full partition pair;
- `2`: ambiguous partition pair requiring lower-level fixed-radius traversal.

The builder also records overflow when the caller supplies a smaller
`pair_capacity` than the full bounded near-pair list.

## Why This Matters

Goal4016 defined the schema. Goal4017 gives us a small exact reference for that
schema.

The next native/device-resident implementation can now be tested against a
known-good Python oracle before any benchmark route is promoted. That reduces
the risk of repeating Goal4009-style hidden correctness changes: if root or
partition convergence changes affect output, the reference builder gives a
small deterministic place to catch the mismatch.

## Boundary

Goal4017 does not authorize public speedup wording.

It is a reference-oracle step. It does not add a native ABI, does not change the
accepted grouped-stream runtime route, and does not authorize release, broad
RT-core, whole-app, true-zero-copy, hidden-dispatch, automatic-partner, or
app-specific-engine claims.

The vocabulary remains app-agnostic: fixed-radius, partition, pair, AABB,
status, and convergence.
