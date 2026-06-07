# Goal3737 - Reusable Shape-Pair Active-Count Executor and RayJoin Perf Packet

Date: 2026-06-07

## Purpose

Goal3734 removed repeated left-shape upload from the generic OptiX shape-pair
active-count route. The next measured bottleneck was still in the repeated hot
query path: every call allocated a relation-flag device buffer, scalar-count
buffer, and launch-parameter buffer before running the same prepared-left
active-count query.

Goal3737 adds a reusable, app-agnostic native executor for this pattern. It keeps
the same generic shape-pair relation traversal and generic active-count
continuation, but prepares reusable native buffers and launch parameters once.
RayJoin uses this executor only from the Python benchmark app layer.

## Implementation

New generic OptiX ABI:

- `rtdl_optix_prepare_shape_pair_relation_active_device_prepared_left_executor`
- `rtdl_optix_run_shape_pair_relation_active_device_prepared_left_executor`
- `rtdl_optix_destroy_shape_pair_relation_active_device_prepared_left_executor`

New native owner:

- `PreparedShapePairRelationActiveCountPreparedLeftExecutor`

New Python runtime surface:

- `PreparedOptixShapePairRelationActiveCountPreparedLeftExecutor`
- `PreparedOptixShapePairRelation.prepare_active_count_prepared_left_executor(...)`

RayJoin app change:

- `PreparedRayJoinOptixShapePairActiveCount.run_packed_left_device_continuation(...)`
  now prepares the generic executor once and measures repeated `executor.run()`
  calls.

## App-Agnostic Boundary

The native engine sees only generic shape-pair relation inputs and a generic
active-count continuation. The new ABI contains no RayJoin, GIS overlay, county,
soil, LSI, or PIP terms. RayJoin remains a Python benchmark-app interpretation
over generic RTDL primitives.

## A5000 Direct Overlay Result

Source artifact:
`docs/reports/goal3737_shape_pair_active_count_executor_direct_a5000/summary.json`

| Chain Count | Pre-Executor Direct Median Sec | Executor Direct Median Sec | Direct Speedup | Row Count |
| ---: | ---: | ---: | ---: | ---: |
| 1024 | 0.000713511 | 0.000380400 | 1.876x | 472 |
| 2048 | 0.001536583 | 0.000612737 | 2.507x | 1305 |
| 4096 | 0.003147002 | 0.001565283 | 2.010x | 4250 |

The 4096 native phase breakdown after the executor:

- traversal: `0.001102414s`
- active scan: `0.000461134s`
- scalar download: `0.000006782s`
- left prepare/upload in the hot path: `0.0s / 0.0s`
- native mode: `active_count_device_continuation_prepared_left_executor`

## RayJoin Safe-Mixed Composite Result

Source artifacts:

- Before executor:
  `docs/reports/goal3737_rayjoin_safe_mixed_prepared_left_cross_size_a5000/summary.json`
- After executor:
  `docs/reports/goal3737_rayjoin_safe_mixed_executor_cross_size_a5000/summary.json`

The conservative safe-mixed route is:

- PIP: CuPy dense scalar count, because the native PIP candidate still mismatches
  on some public-CDB slices.
- LSI: exact RTDL/OptiX prepared segment-pair count.
- Overlay active count: RTDL/OptiX prepared-left shape-pair active-count
  executor.

| Chain Count | All-CuPy Median Sum Sec | Safe-Mixed Executor Sum Sec | Safe-Mixed Speedup vs All-CuPy |
| ---: | ---: | ---: | ---: |
| 1024 | 0.167040193 | 0.000896198 | 186.388x |
| 2048 | 0.356131562 | 0.001219472 | 292.037x |
| 4096 | 1.436036370 | 0.002313084 | 620.832x |

Composite geomean speedup improved from `211.132x` before the executor to
`323.303x` after it. Minimum speedup improved from `137.001x` to `186.388x`.
All counts match.

## 8192 Boundary

An attempted 8192-chain all-CuPy same-contract run failed before the RTDL route
because the dense LSI baseline attempted to allocate about `32.9GB` of flags on
the 24GB A5000. This is a useful scalability signal, but it is not recorded as a
same-contract speedup row because one side cannot execute on this pod.

## Claim Boundary

This is internal engineering evidence only. It does not authorize:

- public RayJoin reproduction claims,
- public RTDL-beats-RayJoin claims,
- broad RT-core speedup claims,
- true zero-copy claims,
- whole-app speedup claims, or
- any release claim.

## Remaining Bottleneck

For the 4096 safe-mixed composite after Goal3737:

- PIP remains a safe CuPy leg at about `0.000785s`.
- LSI is effectively tiny at about `0.000106s`.
- overlay active count remains the dominant RTDL leg at about `0.001422s`.

The next meaningful RayJoin improvement would need to reduce the native
traversal/active-scan work itself or make the PIP native scalar path exact across
the public-CDB slices. Both are legitimate next goals, but Goal3737 already
removed the major repeated allocator/setup overhead without adding app-specific
native logic.
