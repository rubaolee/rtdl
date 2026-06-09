# Goal4067 RT-DBSCAN Partition Pair-Enumeration Option

Date: 2026-06-09

## Purpose

Goal4066 added the generic `device_count_then_emit` partition pair enumerator
as an opt-in memory-pressure preview. Goal4067 exposes that option through the
RT-DBSCAN benchmark app so reviewers can run the partition-convergence
component-size signature modes with either the reviewed mode default or the
exact count-then-emit pair stream.

The new CLI option is:

```bash
--partition-pair-enumeration {mode_default,host,device_bounded_offsets,device_count_then_emit}
```

## Behavior

- `mode_default` preserves each mode's existing reviewed behavior.
- `device_count_then_emit` asks the generic partition-summary preview to run a
  device count pass before emitting the typed pair stream at exact capacity.
- The option is forwarded only to the partition-convergence component-signature
  candidate modes.
- Result metadata records:
  - `partition_pair_enumeration_user_selection`;
  - `partition_pair_enumeration_effective`;
  - `partition_pair_enumeration_explicit_override`;
  - `partition_pair_enumeration_default_route_changed`.

## Boundaries

This is an opt-in preview, not a default-route promotion. It does not make the
partition-convergence candidate the recommended RT-DBSCAN route. It does not
add a native ABI. It does not introduce DBSCAN-specific native engine logic. It
does not authorize release wording, public speedup wording, broad RT-core
wording, whole-app benchmark wording, automatic partner selection, hidden
dispatch, or true-zero-copy wording.

The app still reports the partition-convergence signature modes as
graph-component-contract-only. They are not full DBSCAN core/border/noise
semantics and they still do not materialize Python row dictionaries.

## Validation

Added:

- `tests/goal4067_rt_dbscan_partition_pair_enumeration_option_test.py`.

The test verifies:

- the app, README, and report expose the explicit option;
- invalid `partition_pair_enumeration` values fail before CuPy is needed;
- signature modes still reject Python row materialization before CuPy is needed;
- when CuPy is available, the prepared signature mode can request
  `device_count_then_emit`, matches the graph-component reference signature, and
  keeps all claim boundaries closed.
