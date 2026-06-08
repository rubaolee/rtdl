# Goal3861 - LibRTS Prepared AABB Probe

Date: 2026-06-08

Status: internal diagnostic evidence.

## Purpose

After Goal3859 moved RT-DBSCAN to the faster Numba grouped-stream route, the fresh ten-app A5000 scale packet showed LibRTS-style spatial indexing as one of the largest remaining payload-level timings:

```text
LibRTS scale row payload elapsed_sec: 0.568402 sec
```

Goal3861 decomposes that row. The goal is to decide whether the next meaningful LibRTS work is a real generic runtime primitive or just a Python/app cleanup.

## Evidence

Pod:

```text
ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519
```

Artifact directory:

```text
docs/reports/goal3861_librts_aabb_prepared_probe_a5000/
```

Probe command shape:

```text
python examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py \
  --mode optix_aabb_index \
  --dataset uniform \
  --box-count <N> \
  --query-count <N> \
  --operation <operation> \
  --repeat <R> \
  --warmup <W> \
  --skip-counts
```

## Results

| Row | Payload elapsed sec | Scene prepare sec | Query prepare sec | Prepared query median sec |
| --- | ---: | ---: | ---: | ---: |
| `all_32768_repeat20` | 0.745066 | 0.609786 | 0.105024 | 0.030255 |
| `point_32768_repeat20` | 0.462267 | 0.435167 | 0.019924 | 0.007176 |
| `range_contains_32768_repeat20` | 0.555894 | 0.461145 | 0.087309 | 0.007441 |
| `range_intersects_32768_repeat20` | 0.655870 | 0.552520 | 0.087576 | 0.015773 |
| `all_65536_repeat10` | 1.002599 | 0.686054 | 0.191276 | 0.125268 |

## Interpretation

The result is not a mysterious slow Python continuation.

The existing route already uses the generic OptiX AABB index count path and prepared query buffers. For the 32K all-operation row, the prepared hot query is about `0.030255s`, while scene and query preparation are about `0.714810s` combined. For the 65K all-operation row, the hot query grows to about `0.125268s`, while scene and query preparation are about `0.877330s` combined.

That means the next serious LibRTS improvement is one of two generic runtime changes:

1. A prepared-session accounting/front-door contract that keeps cold build, query-buffer preparation, and hot prepared-query timing separate across all benchmark apps.
2. A generic multi-operation AABB count primitive, especially for box-query workloads where `range_contains` and `range_intersects` currently require separate native launches against the same prepared query buffer.

The second option is a real runtime extension. It should stay generic, with names like `prepared_aabb_index_multi_count_2d`, not LibRTS-specific vocabulary.

## Boundary

This goal does not authorize:

- release action;
- public speedup wording;
- whole-app acceleration claims;
- broad RT-core claims;
- paper reproduction claims;
- true zero-copy claims;
- automatic partner selection claims;
- app-specific native-engine logic.

The accepted conclusion is narrower: LibRTS is currently dominated by cold scene/query preparation in payload-level accounting, and the real generic performance target is prepared-session separation or fused generic AABB multi-operation counts.

