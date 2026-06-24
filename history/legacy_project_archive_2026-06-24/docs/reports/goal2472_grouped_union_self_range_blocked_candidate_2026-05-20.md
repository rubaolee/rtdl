# Goal2472 - Generic grouped-union self-range blocked candidate

Date: 2026-05-20

Status: pod validated as a correct but non-promoted candidate on 2026-05-21.
This adds a generic prepared self-query range surface for OptiX fixed-radius
grouped union and wires RT-DBSCAN to use it only when an explicit blocked
grouped-stream mode is selected. The tested query-range blocking route is not
faster than the default unblocked route and does not authorize a performance
claim.

## Purpose

Goal2470 showed that naive tiny hit segments are not enough, but the runtime
still needs a native surface that can execute grouped continuation over explicit
prepared-search query ranges without repacking query points on the host.

Goal2472 adds that building block:

```text
rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs
```

The symbol is generic. It accepts a prepared fixed-radius 3-D search structure,
`query_start`, `query_count`, radius, optional predicate/fallback workspaces,
parent workspace, optional telemetry, and item count. It launches from the
prepared device search buffer with a query offset, so it remains a prepared
self-query device path.

## Runtime Surface

Python exposes:

```text
PreparedOptixFixedRadiusCountThreshold3D.apply_device_grouped_union_self_range(...)
```

The method supports both:

- all-items mode, where `predicate_flags` and `fallback_candidate_out` are
  omitted;
- predicated mode, where both predicate and fallback workspaces are provided.

It records metadata:

- `native_execution_path = prepared_rt_core_grouped_union_3d_self_query_range`;
- `query_source = prepared_search_points_self_query_device_range`;
- `query_range_policy = explicit_contiguous_prepared_search_range`;
- `grouped_union_blocked_candidate = true`;
- optional Goal2471 telemetry contract when `telemetry_out` is provided.

## Benchmark-App Wiring

The RT-DBSCAN benchmark app adds explicit modes:

```text
optix_rt_core_grouped_stream_blocked_cupy_components_3d
optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d
```

These modes pass `grouped_union_query_block_size` to the prepared
OptiX+CuPy grouped-stream adapter. The default grouped-stream modes are
unchanged and still call the original full self-query symbols.

The blocked modes are not hidden dispatchers and are not default plans. They
exist to collect pod evidence for query-range launch overhead and atomic
telemetry before a deeper blocked/segmented continuation is promoted.

## Boundary

- No DBSCAN-specific native ABI was added.
- No native vocabulary uses DBSCAN, cluster, or min-neighbors semantics.
- The existing default grouped-union path remains unchanged.
- Query blocking is an explicit candidate route, not a release or speed claim.
- This is not yet the final segmented proposal-reduction implementation.
- Pod validation shows range blocking hurts in the tested launch-level form and
  should only remain as scaffolding for the next reduction phase.

## Pod Validation

The successful pod run used:

```text
ssh root@69.30.85.171 -p 22118 -i /Users/rl2025/.ssh/id_ed25519_rtdl_codex
```

Environment:

```text
host: dd76e004260f
gpu: NVIDIA RTX A5000, driver 570.211.01
cuda nvcc: Build cuda_12.8.r12.8/compiler.35583870_0
OptiX headers: NVIDIA/optix-dev v8.0.0
```

The pod tree was a filtered rsync of the local dirty Goal2467-2472 working
tree. Because `.git` was intentionally excluded from that pod sync, report
JSON `source_commit` fields are empty; the local base commit at sync time was
`a9193856547bf692069955a3dbaf6c3e00c09b1b`.

Focused tests passed on the pod:

```text
PYTHONPATH=src:. python -m unittest \
  tests.goal2472_grouped_union_self_range_blocked_candidate_test \
  tests.goal2471_grouped_union_atomic_telemetry_test \
  tests.goal2470_grouped_continuation_segment_sensitivity_test \
  tests.goal2469_rt_dbscan_column_signature_mode_test \
  tests.goal2468_rt_dbscan_overhead_breakdown_instrumentation_test \
  tests.goal2467_blocked_grouped_continuation_design_test \
  tests.goal2465_grouped_union_all_items_intersection_cull_test \
  tests.goal2463_grouped_union_all_items_path_test \
  tests.goal2461_grouped_stream_self_query_device_path_test \
  tests.goal2459_grouped_stream_threshold_capped_core_flags_test \
  tests.goal2457_generic_grouped_stream_continuation_implementation_test
```

Result: 50 tests passed.

The grouped-stream column-signature benchmark was run for unblocked and blocked
query-range modes at 32,768 and 65,536 clustered 3-D points. Values below are
tail medians after discarding repeat 1, with five repeats per case.

| points | mode | block size | total median sec | total / unblocked | grouped native median sec | native / unblocked | signatures match |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 32,768 | unblocked | - | 0.043300 | 1.00x | 0.031052 | 1.00x | true |
| 32,768 | blocked | 8,192 | 0.103427 | 2.39x | 0.086930 | 2.80x | true |
| 32,768 | blocked | 16,384 | 0.065727 | 1.52x | 0.049719 | 1.60x | true |
| 32,768 | blocked | 32,768 | 0.045744 | 1.06x | 0.030972 | 1.00x | true |
| 65,536 | unblocked | - | 0.110211 | 1.00x | 0.082476 | 1.00x | true |
| 65,536 | blocked | 8,192 | 0.312898 | 2.84x | 0.279092 | 3.38x | true |
| 65,536 | blocked | 16,384 | 0.182378 | 1.65x | 0.150733 | 1.83x | true |
| 65,536 | blocked | 32,768 | 0.120403 | 1.09x | 0.089654 | 1.09x | true |

Artifacts:

```text
docs/reports/goal2472_grouped_stream_range_pod_unblocked/
docs/reports/goal2472_grouped_stream_range_pod_blocked_q8192/
docs/reports/goal2472_grouped_stream_range_pod_blocked_q16384/
docs/reports/goal2472_grouped_stream_range_pod_blocked_q32768/
```

## Decision

The range symbol is correct and useful as a generic prepared self-query
building block, but explicit query-range blocking should not be promoted as the
next optimization. Small blocks add too much launch/orchestration overhead and
increase native grouped time. A large 32,768-item block is close to the
unblocked native time at 32,768 points but still loses end-to-end and remains
slower at 65,536 points.

The next optimization should not be "more query chunks." It should use the
Goal2471 telemetry and design a true segmented/proposal-reduction path that
reduces global parent atomic attempts inside a launch, preferably with spatial
or query-local grouping and fail-closed fallback. The native engine vocabulary
must remain generic fixed-radius grouped continuation; RT-DBSCAN remains only
the benchmark stressor.

## Replay Commands

The replayable runner shape is:


```text
PYTHONPATH=src:. python scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --signature-mode column \
  --repeat-count 5 \
  --output-dir docs/reports/goal2472_grouped_stream_range_pod_unblocked

PYTHONPATH=src:. python scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --signature-mode column \
  --repeat-count 5 \
  --grouped-union-query-block-size 8192 \
  --output-dir docs/reports/goal2472_grouped_stream_range_pod_blocked_q8192

PYTHONPATH=src:. python scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --signature-mode column \
  --repeat-count 5 \
  --grouped-union-query-block-size 16384 \
  --output-dir docs/reports/goal2472_grouped_stream_range_pod_blocked_q16384

PYTHONPATH=src:. python scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --signature-mode column \
  --repeat-count 5 \
  --grouped-union-query-block-size 32768 \
  --output-dir docs/reports/goal2472_grouped_stream_range_pod_blocked_q32768
```
