# Goal4016 Partition-Convergence Typed Stream Contract

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal4016 adds the first concrete typed-stream schema for the
partition-convergence direction identified by Goals4007, 4009, 4011, 4012, and
4014.

This does not add a native ABI and does not change the accepted grouped-stream
runtime route. It defines the generic device-column contract that a future
native producer must fill before `partition_convergence_hybrid` can become a
runtime route.

## What Changed

Added:

- `make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract`
  in `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`;
- export through `rtdsl.__init__`;
- `tests/goal4016_partition_convergence_typed_stream_contract_test.py`.

The new typed stream uses producer primitive:

- `fixed_radius_partition_convergence_summary_3d`

It is a `candidate_stream` with `group_ordered` ordering.

## Column Contract

Required point, partition, and near-pair columns:

- `point_partition_ids`;
- `occupied_partition_keys_x`;
- `occupied_partition_keys_y`;
- `occupied_partition_keys_z`;
- `partition_offsets`;
- `partition_counts`;
- `partition_aabb_min_x`;
- `partition_aabb_min_y`;
- `partition_aabb_min_z`;
- `partition_aabb_max_x`;
- `partition_aabb_max_y`;
- `partition_aabb_max_z`;
- `near_pair_left_partition_ids`;
- `near_pair_right_partition_ids`;
- `near_pair_status`.

The standard typed-stream status columns remain required:

- `row_count`;
- `capacity`;
- `overflow`;
- `complete_candidate_coverage`.

## Why This Matters

Goal4014 proved that the feasibility tooling can avoid a dense cell-pair matrix
by using compressed occupied partition keys plus bounded offsets. Goal4016 turns
that implementation shape into a reusable RTDL contract.

The next native implementation slice can now target this schema directly:

1. build partition ids per point;
2. compact occupied partition keys;
3. compute partition offsets/counts and AABBs;
4. enumerate bounded near-partition pairs;
5. classify each pair as safe-full, safe-skip, or ambiguous with visible status;
6. feed the ambiguous boundary work into the existing fixed-radius traversal and
   grouped-union continuation.

## Boundary

Goal4016 does not authorize public speedup wording.

It also does not authorize release, broad RT-core speedup wording, whole-app
acceleration wording, paper-reproduction wording, true-zero-copy wording,
automatic partner/backend selection, hidden dispatch, or app-specific
native-engine logic.

The vocabulary remains app-agnostic: fixed-radius, partition, pair, AABB,
status, and convergence. Application policy stays outside the engine.
