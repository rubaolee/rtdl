# Goal4012 Partition-Convergence Contract After Factor Sweep

Date: 2026-06-08

## Verdict

`accept-with-boundary`

Goal4012 hardens the fixed-radius graph component front-door contract after the
Goal4007 root-read telemetry, Goal4009 root path-halving rejection, and Goal4011
partition-factor sweep.

This is a contract and planning goal. It does not add a native ABI, does not
change the accepted grouped-stream runtime route, and does not authorize public
speedup wording.

## What Changed

The `partition_convergence_hybrid` candidate in
`src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py` now records the
new evidence and implementation constraints:

- `Goal4007`, `Goal4009`, and `Goal4011` are added to the candidate evidence
  goals.
- The candidate explicitly requires a
  `compressed_occupied_partition_key_structure`.
- The candidate explicitly requires `bounded_near_partition_enumeration`.
- The candidate explicitly rejects `no_dense_cell_pair_matrix` as a design
  shortcut.
- The candidate keeps the accepted `readonly_root_find_default_preserved`
  boundary until an explicit deterministic convergence policy exists.
- The candidate rejects hidden root mutation such as
  `hidden_root_path_halving_inside_readonly_find`.
- The candidate records the Goal4011 tested factor signal:
  `radius_x_0.125`.

The exported partition guidance states that the next implementation must use
compressed occupied partition keys with bounded near offsets, not a dense
all-cell-pair matrix.

## Why This Matters

Goal4011 made the next direction sharper. Radius/8 partitions reduced
ambiguous pair upper bounds substantially compared with radius/4, but the
number of occupied partitions also made a dense pair matrix infeasible. Without
this Goal4012 contract update, the front door still pointed to the older
high-level hybrid idea and did not encode the new no-dense-matrix constraint.

The next native slice should therefore start from generic device-resident
partition columns:

1. point partition ids;
2. occupied partition keys;
3. partition offsets;
4. partition counts;
5. partition AABBs;
6. bounded near-partition enumeration;
7. safe-full, safe-skip, and ambiguous status counters;
8. root-read and convergence/staleness telemetry.

This stays app-agnostic. The vocabulary is fixed-radius pairs, partitions,
groups, component roots, convergence, and status counters. It does not introduce
DBSCAN, clustering, epsilon, min-points, or application labels into the native
engine ABI.

## Validation

Added:

- `tests/goal4012_partition_convergence_contract_after_factor_sweep_test.py`

Focused validation checks:

- the candidate strategy remains visible but unsupported as a runtime route;
- the new Goal4007/Goal4009/Goal4011 evidence goals are visible;
- dense cell-pair matrix materialization is explicitly disallowed;
- hidden root path halving remains rejected;
- the candidate plan still returns
  `candidate_requires_native_implementation`;
- `runtime_executable`, `native_abi_added`, release, speedup, RT-core,
  whole-app, true-zero-copy, hidden-dispatch, automatic-partner, and
  app-specific-engine flags all remain false.

## Boundary

Goal4012 does not authorize public speedup wording.

It also does not authorize release, broad RT-core speedup wording, whole-app
acceleration wording, paper-reproduction wording, true-zero-copy wording,
automatic partner/backend selection, or app-specific native-engine logic.

The accepted runtime route remains the existing explicit `grouped_stream`
front door. `partition_convergence_hybrid` remains a fail-closed candidate
until a native/device-resident implementation exists and passes same-contract
parity against grouped stream on dense and sparse pod profiles.
