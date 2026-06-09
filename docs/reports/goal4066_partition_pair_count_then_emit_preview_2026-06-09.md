# Goal4066 Partition Pair Count-Then-Emit Preview

Date: 2026-06-09

## Purpose

Goal4062 showed that prepared partition-summary replay is useful, but the pod
artifact also exposed a memory-shape problem in the current CuPy preview:
`device_bounded_offsets` allocates the conservative bounded-offset upper
capacity even when the visible pair count is much smaller. For example, one
8192-point row allocated capacity for tens of millions of rows while the actual
near-pair stream was under one million rows.

Goal4066 adds an opt-in generic enumeration mode:

`device_count_then_emit`

It uses the existing device bounded-offset RawKernel twice:

1. a count probe with capacity 1 to discover the exact attempted pair count;
2. an emit pass with exact capacity.

This trades an extra pass for a much smaller typed pair stream. It is a
language/runtime memory-pressure improvement, not an app-specific DBSCAN
special case.

## What Changed

- `build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(...)`
  now accepts `pair_enumeration="device_count_then_emit"`.
- Metadata records:
  - `pair_capacity_source: device_exact_count`;
  - `device_pair_count_probe_used: true`;
  - `device_pair_enumeration_used: true`.
- `pair_capacity` is exact: `max(1, pair_count)`.

## Boundaries

This is opt-in preview evidence. It does not change the default
`device_bounded_offsets` route. It does not promote `partition_convergence_hybrid`.
It does not add a native ABI. It does not choose partners automatically. It
does not authorize public speedup wording, release wording, broad RT-core
wording, whole-app benchmark wording, app-specific native engine logic, or
true-zero-copy wording.

## Validation

Added:

- `tests/goal4066_partition_pair_count_then_emit_preview_test.py`.

When CuPy is available, the test compares `device_count_then_emit` with
`device_bounded_offsets` on the same tiny point cloud, validates the summary
against the Python same-contract oracle, and verifies exact capacity plus closed
claim flags.
