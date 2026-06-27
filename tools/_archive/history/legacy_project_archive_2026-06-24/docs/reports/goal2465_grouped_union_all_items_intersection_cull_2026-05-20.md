# Goal2465 - Cull ignored all-items grouped-union intersections before anyhit

Date: 2026-05-20

Status: implemented locally and pod-validated on top of Goal2463.

## Purpose

Goal2463 added a generic all-items-eligible path for prepared fixed-radius
grouped-union continuations. In that path, the anyhit program only unions
`target > source`, because self-query all-items union needs each undirected
radius pair once.

Goal2465 moves that same generic condition earlier: when `all_predicate` is set,
the intersection program returns before `optixReportIntersection(...)` for
`prim <= source`. Those hits would have reached anyhit only to be ignored, so
this reduces anyhit traffic without changing semantics.

This remains app-agnostic: the condition is expressed only in terms of generic
self-query grouped-union indices and the all-items predicate mode.

## What changed

`src/native/optix/rtdl_optix_core.cpp`:

```cpp
const uint32_t source = params.query_index_offset + qidx;
if (params.all_predicate != 0u && prim <= source) {
    return;
}
```

No new native ABI was added. No Python app code was changed.

## Pod validation

Pod:

```text
ssh root@69.30.85.177 -p 22055 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
GPU: NVIDIA RTX A5000
Driver: 570.211.01
CUDA: /usr/local/cuda-12, nvcc 12.8
OptiX SDK: /root/vendor/optix-sdk
Repo baseline: 03d6e140 Goal2463 add grouped union all-items path
```

Build:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12
```

Focused pod tests:

```text
python3 -m unittest \
  tests.goal2463_grouped_union_all_items_path_test \
  tests.goal2461_grouped_stream_self_query_device_path_test

Ran 9 tests in 0.008s - OK
```

## Performance evidence

Artifacts:

- `docs/reports/goal2463_grouped_union_all_items_pod/summary.json`
- `docs/reports/goal2465_grouped_union_all_items_intersection_cull_pod/summary.json`

Same pod, five repeats per point count; tail medians exclude warmup.

| clustered3d points | Goal2463 tail median sec | Goal2465 tail median sec | Ratio | Notes |
| ---: | ---: | ---: | ---: | --- |
| 32,768 | 0.029944 | 0.029642 | 0.990x | mixed predicate row remains on the predicated path |
| 65,536 | 0.085654 | 0.079455 | 0.928x | all-items path culls `target <= source` before anyhit |

Native grouped-union tail medians:

| clustered3d points | Goal2463 native sec | Goal2465 native sec | Ratio |
| ---: | ---: | ---: | ---: |
| 32,768 | 0.029174 | 0.028997 | 0.994x |
| 65,536 | 0.085157 | 0.079016 | 0.928x |

The `65,536` row still reports:

```text
grouped_predicate_mode = all_items_true_no_fallback_candidates
grouped_transfer_mode = prepared_device_search_points_self_grouped_union_all_items_parent_workspace
tiny_smoke.matches_reference = true
```

## Boundary

- This is a micro-optimization inside the generic all-items fixed-radius
  grouped-union path.
- It does not change the mixed predicate continuation path.
- It does not add DBSCAN-specific native ABI.
- It does not authorize broad RT-core speedup claims or release claims.
- The larger remaining design problem is still generic blocked/segmented
  grouped continuation for rows dominated by global atomic pressure.
