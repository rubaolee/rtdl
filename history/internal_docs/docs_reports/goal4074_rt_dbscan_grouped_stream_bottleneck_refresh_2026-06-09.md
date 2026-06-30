# Goal4074 RT-DBSCAN Grouped-Stream Bottleneck Refresh

Date: 2026-06-09

## Status

Implemented, RTX 4000 Ada pod artifact recorded, local tests pass.

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

## Pod Evidence

Artifact:
`docs/reports/goal4074_rt_dbscan_grouped_stream_bottleneck_refresh_pod.json`

Stdout/progress log:
`docs/reports/goal4074_rt_dbscan_grouped_stream_bottleneck_refresh_pod.stdout.txt`

Traceability note: the stdout file records a failed pre-probe on the same
harness, not the successful run that emitted the JSON artifact. The successful
stdout was not retained; the JSON artifact remains the measured pod evidence.

Environment:

- GPU: NVIDIA RTX 4000 Ada Generation
- Source commit: `183c80d3`
- Repeat/warmup: `repeat=6`, `warmup=2`

Recommended-route timing:

| Profile | elapsed sec | native grouped sec | Numba signature sec | native share |
| --- | ---: | ---: | ---: | ---: |
| `clustered3d_65536` | 0.093321 | 0.087859 | 0.005205 | 94.1% |
| `road3d_65536` | 0.036245 | 0.030176 | 0.005428 | 83.3% |

Variant ratios over the recommended route:

| Profile | direct side effect | blocked 32,768 | no same-root culling |
| --- | ---: | ---: | ---: |
| `clustered3d_65536` | 1.006x | 1.258x | 1.218x |
| `road3d_65536` | 0.990x | 1.223x | 1.113x |

Interpretation:

- The current recommended route remains the right default.
- The main bottleneck is still the native grouped-union traversal/union pass, not the Numba signature continuation.
- Explicit query blocking remains worse because it adds native launches/range overhead.
- Same-root culling remains useful; disabling it is slower on both profiles.
- Direct side effects are not a material win: a tiny road-profile improvement is not enough to promote a new default, and the clustered profile is slightly slower.

The next real performance target is a generic grouped-union primitive/runtime improvement that reduces traversal/root-read/candidate work inside the native continuation. Tuning the app-level partition preview or the current Numba signature wrapper will not move the main 65K bottleneck enough.

## Boundary

This report and its artifact do not authorize release, paper reproduction, public speedup, broad RT-core speedup, whole-app acceleration, hidden dispatch, automatic partner selection, app-specific native-engine logic, native ABI addition, or true-zero-copy claims.
