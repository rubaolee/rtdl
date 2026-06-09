# Goal4074 RT-DBSCAN Grouped-Stream Bottleneck Refresh

Date: 2026-06-09

## Status

Implemented as a current-head telemetry harness; pod artifact pending.

## Purpose

Goals4070-4071 and the independent Goal4072/4073 reviews closed the partition-preview lane:

- `device_count_then_emit` is a useful memory-pressure option, not a default speed path.
- The recommended RT-DBSCAN route remains `optix_rt_core_grouped_stream_numba_column_signature_3d`.
- The next useful work must target the recommended RT-core grouped-stream route itself.

Goal4074 adds a focused harness for that target. It runs the recommended route and three existing variants under the same repeat/warmup protocol, then records host-observed timing, native grouped-stream timing, count-threshold native timing, signature timing, query-block metadata, and claim-boundary flags.

## Variants

| Variant | Mode | Purpose |
| --- | --- | --- |
| `recommended_unblocked` | `optix_rt_core_grouped_stream_numba_column_signature_3d` | Current recommended route. |
| `direct_side_effect` | same mode with `grouped_union_direct_side_effect=True` | Recheck whether direct side effects help current head. |
| `blocked_32768` | `optix_rt_core_grouped_stream_blocked_numba_column_signature_3d` | Recheck explicit query blocking with fair warmup. |
| `no_same_root_culling` | same mode with `grouped_union_same_root_culling=False` | Reconfirm same-root culling is still useful. |

## Profiles

- `clustered3d_65536`
- `road3d_65536`

These profiles are deliberately larger than the small option tests while staying bounded enough for repeatable pod runs.

## Expected Interpretation

The harness is diagnostic. It is designed to answer:

1. Is the grouped-stream native pass still the dominant cost?
2. Is Numba signature/reset overhead material enough to tune next?
3. Do existing toggles (`direct_side_effect`, blocked ranges, same-root culling off) become helpful on current head?
4. Does route correctness remain stable by normalized component-size signature?

If the native grouped-stream pass still dominates, the next real primitive work should be a generic grouped-union continuation improvement, not more app-level partition-preview tuning.

## Boundary

This report and its artifact do not authorize release, paper reproduction, public speedup, broad RT-core speedup, whole-app acceleration, hidden dispatch, automatic partner selection, app-specific native-engine logic, native ABI addition, or true-zero-copy claims.

