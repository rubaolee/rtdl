# Goal2445 RT-DBSCAN Prepared Chunk Offsets Pod Smoke

Date: 2026-05-19

Status: pod-smoked, with boundary.

## Purpose

Goal2444 prepares each chunk's fixed-radius adjacency `edge_offsets` once after
exact degree counts are known. Goal2445 verifies that behavior on hardware with
a repeated prepared-handle run.

## Pod

```text
ssh root@69.30.85.177 -p 22055 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

The pod checkout was reset to:

```text
2d938df526ff4b68e6831a926fb2d8262e574ffb
```

Runtime:

```text
RTDL_OPTIX_LIBRARY=/root/rtdl_goal2415/build/librtdl_optix.so
CUDA_HOME=/usr/local/cuda-12
RTDL_OPTIX_PTX_ARCH=compute_86
```

Artifact:

- `docs/reports/goal2445_rt_dbscan_prepared_chunk_offsets_pod_smoke/summary.json`

## Result

Dataset:

```text
clustered3d, 32768 points, chunk edge budget 8000000
```

| Phase | Runtime (s) | Notes |
| --- | ---: | --- |
| prepare handle | 1.285382 | counts exact degrees, plans 18 chunks, prepares offset columns |
| repeat 1 | 0.696896 | first chunked run; `prepared_chunk_edge_offsets_reused=false` |
| repeat 2 | 0.339079 | repeated chunked run; `prepared_chunk_edge_offsets_reused=true` |

Both repeats produced the same component signature:

```text
4 clusters of 8192 points, 32767 core points, 0 noise points
```

The runtime kept the Goal2442 memory cap:

```text
max_chunk_directed_edge_count = 7,999,889 <= 8,000,000
```

## Boundary

This is prepared-handle evidence for offset reuse. It is not a whole-app speedup claim.
It is not a DBSCAN paper reproduction claim, and not a release claim.

The implementation still allocates `neighbor_indices` per chunk. That is
intentional: reusing one neighbor-index workspace across chunks could create a
cross-stream reuse race unless OptiX/CuPy stream ordering is proven separately.

## Verdict

`accept-with-boundary`.
