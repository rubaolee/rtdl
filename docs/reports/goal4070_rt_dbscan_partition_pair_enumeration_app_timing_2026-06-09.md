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
- `docs/reports/goal4070_rt_dbscan_partition_pair_enumeration_app_timing_pod.json`.
- `docs/reports/goal4070_rt_dbscan_partition_pair_enumeration_app_timing_pod.stdout.txt`.

The script verifies that `mode_default` and `device_count_then_emit` return the
same component-size signature for each profile before recording timing rows.

## Pod Evidence

Pod timing was recorded on RTX 4000 Ada at source commit `96efd0b3` with three
measured repetitions per row. All 12 rows preserved the same component-size
signature and kept all claim flags closed.

| App Mode | Profile | Capacity Reduction | Time Ratio Count/Default |
| --- | --- | ---: | ---: |
| `partner_cupy_partition_convergence_component_signature_3d` | `clustered3d_1024` | 71.21x | 1.108x |
| `partner_cupy_partition_convergence_component_signature_3d` | `road3d_1024` | 209.35x | 1.088x |
| `partner_cupy_partition_convergence_component_signature_3d` | `clustered3d_4096` | 21.27x | 1.086x |
| `partner_cupy_partition_convergence_component_signature_3d` | `road3d_4096` | 60.11x | 1.075x |
| `partner_cupy_partition_convergence_component_signature_3d` | `clustered3d_8192` | 13.13x | 1.067x |
| `partner_cupy_partition_convergence_component_signature_3d` | `road3d_8192` | 34.47x | 0.931x |
| `partner_cupy_prepared_partition_convergence_component_signature_3d` | `clustered3d_1024` | 71.21x | 1.100x |
| `partner_cupy_prepared_partition_convergence_component_signature_3d` | `road3d_1024` | 209.35x | 1.088x |
| `partner_cupy_prepared_partition_convergence_component_signature_3d` | `clustered3d_4096` | 21.27x | 1.089x |
| `partner_cupy_prepared_partition_convergence_component_signature_3d` | `road3d_4096` | 60.11x | 1.072x |
| `partner_cupy_prepared_partition_convergence_component_signature_3d` | `clustered3d_8192` | 13.13x | 1.086x |
| `partner_cupy_prepared_partition_convergence_component_signature_3d` | `road3d_8192` | 34.47x | 1.035x |

Conclusion: `device_count_then_emit` is a useful memory-pressure option
(13.13x-209.35x lower pair-stream capacity in this packet), but it is not a
default performance win at the app level. The extra device count pass is usually
5%-11% slower here, with one large road-shaped row faster. The correct policy is
therefore explicit user selection when capacity pressure matters, not automatic
promotion.
