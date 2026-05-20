# Goal2463 - Generic all-items grouped-union path for dense fixed-radius continuations

Date: 2026-05-20

Status: implemented locally and pod-validated on the Goal2461 grouped-stream path.

## Purpose

Goal2461 removed the host repack/upload from the RT-DBSCAN grouped-stream
continuation by letting the prepared OptiX search buffer serve as the query
buffer. The remaining hot phase was the native grouped-union anyhit continuation:
every fixed-radius hit still loaded predicate flags and maintained a fallback
candidate workspace even when the count-threshold pass had proved that every
point satisfied the predicate.

Goal2463 adds a generic all-items-eligible mode to the same grouped-union
primitive. It is not a DBSCAN native ABI and does not add app vocabulary to the
engine. The optimization is simply:

- if every item is predicate-true, pass null predicate/fallback pointers into the
  existing self-query grouped-union native entry;
- the native launch parameter records `all_predicate=1`;
- anyhit unions every `target > source` radius hit without predicate loads or
  fallback-candidate writes;
- the Python partner adapter still labels components with the generic CuPy
  continuation kernel and records the explicit execution path.

The non-uniform predicate path remains unchanged and still captures one fallback
candidate for predicate-false rows.

## What changed

- `src/native/optix/rtdl_optix_core.cpp`
  - Added `all_predicate` to the grouped-union launch params.
  - Added an anyhit branch for all-items mode:
    `target > source -> union_grouped_min_root(parent_out, source, target)`.
- `src/native/optix/rtdl_optix_workloads.cpp`
  - Mirrors the launch-param field.
  - Sets `all_predicate` when `predicate_flags == nullptr`.
  - Allows the existing generic self-query symbol to accept null
    predicate/fallback pointers only for all-items mode.
- `src/rtdsl/optix_runtime.py`
  - Added `PreparedOptixFixedRadiusCountThreshold3D.apply_device_grouped_union_all_self(...)`.
  - Reuses the existing generic native symbol:
    `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs`.
- `src/rtdsl/partner_adapters.py`
  - Caches whether all core flags are true after the threshold-capped count pass.
  - Uses the all-items path only when that cached predicate is uniformly true.
  - Keeps the predicated fallback path for mixed core/border/noise workloads.

## Pod validation

Pod:

```text
ssh root@69.30.85.177 -p 22055 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
GPU: NVIDIA RTX A5000
Driver: 570.211.01
CUDA: /usr/local/cuda-12, nvcc 12.8
OptiX SDK: /root/vendor/optix-sdk
Repo baseline: 80f10d01 Goal2461 add grouped stream self-query path
```

Build:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12
```

Focused tests on the pod:

```text
python3 -m unittest \
  tests.goal2461_grouped_stream_self_query_device_path_test \
  tests.goal2459_grouped_stream_threshold_capped_core_flags_test \
  tests.goal2457_generic_grouped_stream_continuation_implementation_test

Ran 14 tests in 0.031s - OK
```

## Performance evidence

Artifacts:

- `docs/reports/goal2463_grouped_union_baseline_pod/summary.json`
- `docs/reports/goal2463_grouped_union_all_items_pod/summary.json`

Same pod, same codebase baseline, same probe shape, five repeats per point count;
tail medians exclude the first warmup repeat.

| clustered3d points | Goal2461 baseline tail median sec | Goal2463 tail median sec | Ratio | Notes |
| ---: | ---: | ---: | ---: | --- |
| 32,768 | 0.029410 | 0.029944 | 1.018x | one point is not core, so the old predicated path is correctly used |
| 65,536 | 0.096906 | 0.085654 | 0.884x | all points are core, so all-items mode is used |

Native grouped-union tail medians:

| clustered3d points | Goal2461 baseline native sec | Goal2463 native sec | Ratio |
| ---: | ---: | ---: | ---: |
| 32,768 | 0.028900 | 0.029174 | 1.009x |
| 65,536 | 0.096254 | 0.085157 | 0.885x |

The `65,536` row reports:

```text
grouped_predicate_mode = all_items_true_no_fallback_candidates
grouped_transfer_mode = prepared_device_search_points_self_grouped_union_all_items_parent_workspace
tiny_smoke.matches_reference = true
```

## Rejected experiment

Before Goal2463, a path-compressing root lookup experiment was A/B tested on the
same pod. It slightly helped one 32k sample but slowed the 65k row
(`~0.0969s -> ~0.1025s` tail median), so it was reverted and is not part of the
implementation. The bottleneck is broader global atomic pressure, not just root
lookup depth.

## Boundary

- This is a generic fixed-radius grouped continuation optimization, not a
  DBSCAN-specific native endpoint.
- It only helps workloads whose predicate is uniformly true; mixed core/border
  workloads retain the predicated path.
- It does not authorize broad RT-core speedup claims or v2.0/v2.2 release
  claims by itself.
- The next deeper optimization is still a more general blocked/segmented
  grouped-continuation design to reduce global atomic pressure.
