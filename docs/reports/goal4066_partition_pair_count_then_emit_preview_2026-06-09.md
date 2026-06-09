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
- `scripts/goal4066_pair_count_then_emit_timing.py`.
- `docs/reports/goal4066_pair_count_then_emit_timing_pod.json`.
- `docs/reports/goal4066_pair_count_then_emit_timing_pod.stdout.txt`.

When CuPy is available, the test compares `device_count_then_emit` with
`device_bounded_offsets` on the same tiny point cloud, validates the summary
against the Python same-contract oracle, and verifies exact capacity plus closed
claim flags.

The timing script compares the existing upper-bound allocation mode with the new
count-then-emit mode. The expected success criterion is not necessarily lower
runtime, because the new path intentionally performs two device passes. The key
runtime-design question is whether exact capacity substantially reduces memory
pressure while preserving the same pair stream.

Pod evidence at source commit `1f86bcd1` on RTX 4000 Ada:

| Profile | Points | Capacity Reduction | Time Ratio Count/Bounded Median |
| --- | ---: | ---: | ---: |
| clustered3d_1024 | 1024 | 111.50x | 1.035x |
| road3d_1024 | 1024 | 657.62x | 1.059x |
| clustered3d_4096 | 4096 | 70.19x | 1.027x |
| road3d_4096 | 4096 | 650.91x | 1.041x |
| clustered3d_8192 | 8192 | 61.56x | 0.999x |
| road3d_8192 | 8192 | 652.10x | 0.983x |

All six rows preserve the same pair stream and closed claim flags. The result is
therefore a memory-pressure win with near-parity timing, not a broad speedup
claim.
