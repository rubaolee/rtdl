# Goal2468 - RT-DBSCAN grouped-stream overhead-breakdown instrumentation

Date: 2026-05-20

Status: local instrumentation only. This goal adds measurement plumbing for the
next pod run; it includes no new pod measurement and does not authorize a performance claim.

## Purpose

Goal2467 showed that the latest Blackwell pod baseline has a large gap between
the native grouped RT primitive and the full warm app elapsed time:

| clustered3d points | full warm elapsed | native grouped RT |
| ---: | ---: | ---: |
| 32,768 | 0.070247 sec | 0.024729 sec |
| 65,536 | 0.163915 sec | 0.069710 sec |

The next useful local step is to attribute this gap before changing the
algorithm again. The instrumentation added here records host-observed phase
timings around the grouped-stream path without adding synchronization inside
the native hot path.

## Added Timing Schema

Schema:

```text
rt_dbscan_grouped_stream_host_overhead_breakdown_v1
```

The benchmark app now records `metadata["benchmark_timing_breakdown"]` for
`optix_rt_core_grouped_stream_cupy_components_3d` one-shot runs. The replayable
pod runner records `repeat_rows[*]["timing_breakdown"]` for warm-repeat
analysis and `tail_timing_breakdown_median_sec` for direct summary reading.

Host-observed phase fields:

- `prepare_sec` in the one-shot benchmark app only;
- `adapter_run_sec`;
- `rows_materialization_sec`;
- `densify_cluster_labels_sec`;
- `signature_sec` in the repeat runner only.

Derived fields:

- `grouped_native_sec`;
- `count_native_current_run_sec`;
- `known_native_current_run_sec`;
- `adapter_non_native_estimated_sec`;
- `known_host_phase_sec`;
- `unattributed_elapsed_sec`.

`count_native_current_run_sec` is treated as zero when
`core_flag_cache_reused = true`, because cached count metadata describes the
previous cache-fill run and should not be charged to the current warm repeat.

## Boundary

This is diagnostic measurement plumbing:

- it does not add a native ABI;
- it does not change grouped-stream semantics;
- it does not add synchronization inside native RT traversal;
- it does not rewrite historical benchmark artifacts;
- it does not authorize a paper, broad RT-core, or whole-app speedup claim.

## Next Pod Use

When a pod is available, rerun:

```text
python3 scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --output-dir docs/reports/goal2468_grouped_stream_overhead_pod \
  --point-count 32768 \
  --point-count 65536 \
  --repeat-count 5
```

The useful readout is the tail-median breakdown for:

- `adapter_non_native_estimated_sec`;
- `rows_materialization_sec`;
- `densify_cluster_labels_sec`;
- `signature_sec`;
- `unattributed_elapsed_sec`.

The runner now computes these medians in
`summaries[*]["tail_timing_breakdown_median_sec"]`; no manual JSON
post-processing is required for the first read.

Only after that attribution should we decide whether to optimize label
materialization, Python/CuPy orchestration, or the native grouped continuation
itself.
