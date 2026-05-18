# Goal2353 - RTNN v2.2 Pod Baseline And RTDL Gap Check

Date: 2026-05-18

Status: RTX pod baseline collected; RTDL v2.2 primitive work still pending.

## Purpose

This goal moves the RTNN v2.2 campaign from local smoke work to an RTX pod. The intent is not to claim RTDL speedup yet. The intent is to prove that:

1. RTDL OptiX can build and run on the pod.
2. The external RTNN implementation can build and run on the same pod.
3. RTNN's measured behavior tells us which generic RTDL primitive/runtime work matters next.

## Pod And Toolchain

| Item | Value |
| --- | --- |
| SSH endpoint | `ssh root@69.30.85.236 -p 22170 -i id_ed25519_rtdl_codex` |
| Pod hostname | `Li-1` / container `bae6447764b6` |
| OS | Ubuntu 24.04.3 LTS |
| GPU | NVIDIA RTX A5000 |
| Driver | 570.211.01 |
| GPU memory | 24564 MiB |
| CUDA | 12.8.93 under `/usr/local/cuda` |
| RTDL checkout | `/root/work/rtdl_v2_2_rtnn_pod` |
| RTDL commit for final rows | `e41e5388` |
| RTDL OptiX SDK | `/root/vendor/optix-sdk-9.0` |
| RTNN checkout | `/root/work/rtdl_v2_2_rtnn_pod/scratch/rtnn_goal2351` |
| RTNN commit | `5532e70` |

## Setup Findings

The pod initially cloned NVIDIA's latest OptiX SDK headers, which reported OptiX `(9, 1, 0)`. The RTDL library loaded, but the first OptiX launch failed with `OptiX error: Unsupported ABI version` on driver 570.211.01. Rebuilding RTDL against the `v9.0.0` OptiX SDK tag fixed the runtime ABI issue:

```text
OPTIX_VERSION (9, 0, 0)
```

The external RTNN code also needed CUDA 12 compatibility handling. The Goal2348 `patch-rtnn-cuda12` helper applied seven external-checkout-only edits:

- missing Thrust includes in `thrust_helper.cu`;
- missing `thrust/host_vector.h` in `sort.cpp`;
- host-side `__CUDA_ARCH_LIST__=600` namespace alignment for Thrust declarations;
- `uint_as_float` / `float_as_uint` rewritten to `__uint_as_float` / `__float_as_uint` for NVRTC.

These edits are only for the disposable external RTNN checkout. They do not change RTDL source and do not change RTNN's neighbor-search algorithm.

## Collected Rows

Artifacts are saved under:

```text
docs/reports/goal2353_rtnn_pod/
```

Generated inputs:

| Artifact | Points | Dimension | Seed |
| --- | ---: | ---: | ---: |
| `ppp_3d_65536_generate.json` | 65,536 | 3 | 2353 |
| `ppp_3d_262144_generate.json` | 262,144 | 3 | 2354 |
| `ppp_2d_8192_generate.json` | 8,192 | 2 | 2355 |

RTNN baseline rows:

| Row | Return | Wall sec | RTNN total search ms | Sort/partition ms | Search compute ms | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `rtnn_radius_3d_65536_r002_k50_partitioned.json` | 0 | 14.183803 | 12442.500 | 12427.100 | 0.167 | cold/pathological auto-partition artifact |
| `rtnn_radius_3d_65536_r002_k50_partitioned_warm2.json` | 0 | 1.357491 | 216.144 | 206.409 | 0.175 | use as the steady row |
| `rtnn_radius_3d_262144_r002_k50_partitioned.json` | 0 | 1.492156 | 486.824 | 458.400 | 0.257 | successful large radius row |
| `rtnn_radius_3d_262144_r002_k50_partitioned_warm2.json` | 0 | 1.527938 | 514.120 | 469.512 | 1.993 | successful warm repeat |
| `rtnn_knn_3d_65536_r005_k5_exact_partitioned.json` | 0 | 1.757467 | 833.696 | 797.862 | 0.208 | exact KNN row |
| `rtnn_knn_3d_262144_r005_k5_exact_partitioned.json` | 0 | 1.930505 | 855.025 | 796.663 | 0.315 | exact KNN row |
| `rtnn_knn_3d_262144_r005_k5_approx2_partitioned.json` | 0 | 1.953061 | 851.582 | 795.735 | 0.173 | approximate policy row |

Current RTDL smoke rows:

| Row | OK | Wall sec | Scope |
| --- | --- | ---: | --- |
| `rtdl_current_2d_fixed_radius_smoke_8192.json` | true | 1.119771 | current 2D fixed-radius count-threshold smoke only |

## What This Shows

RTNN is now a runnable same-hardware external baseline for the v2.2 campaign. On the RTX A5000, the measured RT traversal/search compute component is very small compared with RTNN's sorting, partitioning, batching, and data-structure work. That is the important design signal for RTDL:

- adding a raw traversal call is not enough;
- a useful RTDL v2.2 nearest-neighbor primitive needs prepared 3D bounded neighbor search;
- the primitive must expose radius, `k_max`, exact/approx policy, partitioning/batching policy, overflow handling, and output shape;
- the runtime must surface telemetry that separates setup, sort/partition, traversal, copy, and total time.

Current RTDL does expose a 3D fixed-radius neighbor DSL path, but the current OptiX-runtime implementation is a CUDA fixed-radius neighbor kernel rather than an RTNN-style prepared RT-core traversal with partitioning/batching telemetry. The successful 2D RTDL row above therefore proves pod OptiX health, not RTNN parity. A separate current-3D RTDL row should be collected as a CUDA-core baseline before claiming any v2.2 improvement.

## Claim Boundary

This goal does not authorize:

- an RTDL speedup claim over RTNN;
- a broad RT-core speedup claim;
- a claim that RTDL already reproduces RTNN;
- a claim that the current 3D fixed-radius RTDL path is RT-core accelerated;
- a v2.2 release claim.

It does authorize the narrower engineering conclusion that the external RTNN baseline and RTDL OptiX runtime are both runnable on the same RTX A5000 pod, and that the next RTDL v2.2 work should target a generic 3D bounded-neighbor primitive rather than app-specific nearest-neighbor code.

## Next Engineering Step

Implement the first RTDL v2.2 generic primitive proposal:

```text
prepared_bounded_neighbor_search_3d
```

Required contract:

- point/query columns in 3D;
- radius and `k_max`;
- exact/approx policy;
- prepared-handle reuse for repeated queries;
- bounded neighbor id/distance/count output;
- overflow/limit telemetry;
- phase timing compatible with RTNN's timing vocabulary.

This keeps RTDL app-agnostic while letting the RTNN benchmark drive real runtime design.
