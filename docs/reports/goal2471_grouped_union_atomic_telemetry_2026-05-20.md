# Goal2471 - Generic grouped-union atomic telemetry

Date: 2026-05-20

Status: pod validated on 2026-05-21. This adds optional native telemetry
plumbing for prepared OptiX fixed-radius grouped-union self-query paths. It is
not an optimization and does not authorize a performance claim.

## Purpose

Goal2470 showed that a naive tiny-segment continuation prototype is unlikely
to reduce enough global parent atomic pressure. Before changing scheduling or
adding proposal buffers, the native path needs measured counters for the
current grouped-union behavior.

Goal2471 adds an optional generic telemetry symbol:

```text
rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs_with_telemetry
```

The existing non-telemetry symbol is unchanged and remains the default runtime
path. Telemetry is caller-owned and explicit.

## Counter Contract

The caller passes a contiguous CUDA `uint64[4]` device column:

```text
telemetry[0] = parent_atomic_attempts
telemetry[1] = parent_atomic_successes
telemetry[2] = fallback_atomic_attempts
telemetry[3] = fallback_atomic_successes
```

Parent counters measure `atomicMin` attempts/successes inside the generic
grouped-union parent update. Fallback counters measure the optional
predicate-false border-candidate `atomicMin` path.

## Boundary

- Existing grouped-union symbols and default benchmark paths are unchanged.
- Telemetry adds device atomics and should not be used for performance timing
  except when explicitly measuring instrumentation overhead.
- The vocabulary is generic: fixed radius, grouped union, parent, fallback,
  telemetry.
- No DBSCAN-specific native ABI is introduced.
- Pod validation confirms the counters execute on the OptiX path, but this
  remains instrumentation and not a performance optimization.

## Local Validation

The following local checks passed on 2026-05-20:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest \
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

Result: 42 tests passed.

The focused Goal2457-2472 suite was rerun on the 2026-05-21 pod after Goal2472
was added:

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

Syntax and diff hygiene also passed:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m py_compile \
  src/rtdsl/optix_runtime.py \
  examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  tests/goal2471_grouped_union_atomic_telemetry_test.py \
  tests/goal2470_grouped_continuation_segment_sensitivity_test.py \
  tests/goal2469_rt_dbscan_column_signature_mode_test.py

git diff --check
```

The earlier provided pod endpoint `root@213.173.110.198:21453` was tested with the
RTDL key `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`, but SSH returned
`Connection refused`. No OptiX runtime validation was collected from that pod.

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
tree. Because `.git` was intentionally excluded from that pod sync,
`source_commit` in the smoke JSON is empty; the local base commit at sync time
was `a9193856547bf692069955a3dbaf6c3e00c09b1b`.

Command:

```text
PYTHONPATH=src:. python scripts/goal2471_grouped_union_telemetry_pod_smoke.py \
  --output docs/reports/goal2471_grouped_union_telemetry_pod_smoke.json
```

Artifact:

```text
docs/reports/goal2471_grouped_union_telemetry_pod_smoke.json
```

Result: `status = pass`.

Observed counters:

| mode | radius | telemetry[0] parent attempts | telemetry[1] parent successes | telemetry[2] fallback attempts | telemetry[3] fallback successes |
| --- | ---: | ---: | ---: | ---: | ---: |
| all-items | 0.5 | 1120 | 511 | 0 | 0 |
| predicated | 0.5 | 768 | 254 | 21763 | 1217 |

The all-items path exercised parent atomics and kept fallback counters zero.
The predicated path exercised both parent atomics and fallback atomics. This is
the required runtime proof for using Goal2471 counters in later optimization
studies.

The smoke records the following checks:

1. allocates `uint64[4]` telemetry on CuPy;
2. calls `apply_device_grouped_union_all_self(..., telemetry_out=telemetry)`;
3. verifies parent attempts and successes are positive;
4. verifies fallback counters stay zero for all-items mode;
5. runs predicate/fallback mode and checks fallback attempts become positive;
6. records telemetry-on versus telemetry-off timing for overhead context;
7. confirms existing non-telemetry paths still pass the focused Goal2457-2472
   tests.
