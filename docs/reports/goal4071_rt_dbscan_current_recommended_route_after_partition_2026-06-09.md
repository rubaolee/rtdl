# Goal4071 RT-DBSCAN Current Recommended Route After Partition Preview

Date: 2026-06-09

## Purpose

Goals4065-4070 explored the partition-convergence component-signature preview
and the `device_count_then_emit` memory-pressure option. Goal4071 refreshes the
RT-DBSCAN route-positioning evidence after that work: the key question is
whether the partition preview should displace the current RT-core grouped-stream
Numba signature route.

## Routes Compared

The runner compares four same-profile routes on `clustered3d`, 65,536 points:

- recommended RT-core grouped stream + Numba direct component-size signature;
- prepared partition-convergence CuPy signature with `device_count_then_emit`;
- Numba prepared grid partner baseline;
- CuPy prepared grid partner baseline.

## Boundary

This is route-positioning evidence only. It does not authorize release wording,
paper reproduction, public speedup wording, broad RT-core wording, whole-app
benchmark wording, hidden dispatch, automatic partner selection, app-specific
native engine logic, native ABI addition, or true-zero-copy wording.

## Validation

Added:

- `scripts/goal4071_rt_dbscan_current_recommended_route_after_partition.py`.
- `tests/goal4071_rt_dbscan_current_recommended_route_after_partition_test.py`.

The runner records whether each candidate returns the same component-size
signature as the recommended route, and how much faster the recommended route is
than each candidate on the same profile.
