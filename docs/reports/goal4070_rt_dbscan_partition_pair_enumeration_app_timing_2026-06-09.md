# Goal4070 RT-DBSCAN Partition Pair-Enumeration App Timing

Date: 2026-06-09

## Purpose

Goal4066 showed that `device_count_then_emit` greatly reduces partition pair
capacity at the primitive-preview layer. Goal4067 exposed that selection through
the RT-DBSCAN benchmark app. Goal4070 measures whether the option remains useful
at the app-mode level.

The timing packet compares:

- `partner_cupy_partition_convergence_component_signature_3d`;
- `partner_cupy_prepared_partition_convergence_component_signature_3d`;

under:

- `partition_pair_enumeration=mode_default`;
- `partition_pair_enumeration=device_count_then_emit`.

## Boundaries

This is an internal app-level timing packet. It does not promote the
partition-convergence candidate. It does not add a native ABI. It does not
authorize release wording, public speedup wording, broad RT-core wording,
whole-app benchmark wording, hidden dispatch, automatic partner selection,
app-specific native engine logic, or true-zero-copy wording.

The measured app modes still return only the graph-component size signature.
They are not full DBSCAN core/border/noise semantics and do not use RT cores.

## Validation

Added:

- `scripts/goal4070_rt_dbscan_partition_pair_enumeration_app_timing.py`.
- `tests/goal4070_rt_dbscan_partition_pair_enumeration_app_timing_test.py`.

The script verifies that `mode_default` and `device_count_then_emit` return the
same component-size signature for each profile before recording timing rows.
