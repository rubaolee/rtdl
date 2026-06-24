# Goal2442 RT-DBSCAN Adaptive Chunk Budget Pod Smoke

Date: 2026-05-19

Status: pod-smoked, with boundary.

## Purpose

Goal2441 made the chunked OptiX adjacency continuation degree-budget-aware.
Goal2442 verifies that behavior on hardware.

## Pod

```text
ssh root@69.30.85.177 -p 22055 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

The pod checkout was reset to:

```text
931275f6846b2e6ba19f336e814089783584d4d7
```

Runtime:

```text
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2415/build/librtdl_optix.so
CUDA_HOME=/usr/local/cuda-12
RTDL_OPTIX_PTX_ARCH=compute_86
```

Artifacts:

- `docs/reports/goal2442_rt_dbscan_adaptive_chunk_budget_pod_smoke/clustered32768_chunk_budget_8000000.json`
- `docs/reports/goal2442_rt_dbscan_adaptive_chunk_budget_pod_smoke/summary.json`

## Result

Command shape:

```bash
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py \
  --mode optix_rt_core_chunked_adjacency_cupy_components_3d \
  --dataset clustered3d \
  --point-count 32768 \
  --chunk-adjacency-edge-budget 8000000 \
  --no-validation
```

| Points | Total directed edges | Edge budget | Count chunks | Adjacency chunks | Max chunk edges | Runtime (s) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32,768 | 136,345,984 | 8,000,000 | 8 | 18 | 7,999,889 | 1.982988 |

The important result is the max chunk size:

```text
7,999,889 <= 8,000,000
```

This proves the runtime now splits adjacency chunks after exact degree counts
are known. The older fixed 4096-point chunk policy would have produced 8
adjacency chunks for this row; the adaptive budget produced 18 smaller chunks.

## Boundary

This is a memory-control result, not a speedup result. It deliberately used
`--no-validation`; correctness for the underlying chunked continuation is
already covered by Goal2433/Goal2435. This goal only validates the new adaptive
chunk-budget behavior.

This goal does not add native DBSCAN ABI, does not change native engine
semantics, and does not authorize paper reproduction, broad RT-core speedup, or
release claims.

## Verdict

`accept-with-boundary`.
