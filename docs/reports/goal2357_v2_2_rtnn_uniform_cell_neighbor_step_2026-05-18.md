# Goal2357 - RTNN-Informed Uniform-Cell 3D Neighbor Step

Date: 2026-05-18

Status: implemented and pod-tested; accepted as a bounded v2.2 improvement, not RTNN parity.

## Purpose

Goal2353 showed that RTDL's current 3D fixed-radius neighbor path was functional but still shaped like a CUDA all-pairs kernel behind the OptiX runtime wrapper. Goal2357 tests the first v2.2 runtime improvement inspired by RTNN: use a generic spatial preparation step before bounded neighbor collection.

The implementation remains app-agnostic. It does not introduce RTNN-specific names, datasets, or native app continuations.

## Implementation

The OptiX backend now has three 3D fixed-radius neighbor execution paths:

| Path | Selection | Purpose |
| --- | --- | --- |
| Generic uniform-cell bounded-neighbor traversal | default | v2.2 current path for `fixed_radius_neighbors` on 3D points |
| Simple custom-primitive OptiX traversal | `RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_RT=1` | diagnostic RT-core probe, not default |
| Older all-pairs CUDA kernel | `RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_CUDA=1` | compatibility/performance comparison fallback |

The default path builds a dense uniform cell index over the search points using `cell_size = radius`, scans the 27 neighboring cells per query, keeps a bounded per-query top-K set, writes per-query populated counts, and normalizes exact distances on the host. Dense `id == index` inputs use a direct-index normalization fast path; arbitrary IDs keep the conservative map/sort fallback.

This is a generic neighbor primitive, not an app-specific nearest-neighbor implementation.

## Pod Evidence

| Item | Value |
| --- | --- |
| SSH endpoint | `ssh root@69.30.85.236 -p 22170 -i id_ed25519_rtdl_codex` |
| Pod | `bae6447764b6` / `Li-1` |
| GPU | NVIDIA RTX A5000 |
| Driver | 570.211.01 |
| CUDA | 12.8.93 |
| OptiX SDK | `/root/vendor/optix-sdk-9.0` |
| Correctness | `tests.goal311_v0_5_optix_3d_nn_test`: 4/4 pass |

Artifacts are under:

```text
docs/reports/goal2357_rtdl_3d_neighbor_rt/
```

## Same-Protocol Warm Raw Rows

The most useful rows use `result_mode=raw` and `repeat=3`, because RTNN's best comparison rows are warm rows and Python dict materialization is not the intended continuation surface for large neighbor streams.

| Input | Old CUDA warm/raw sec | New uniform-cell warm/raw sec | RTDL delta | RTNN warm sec | RTDL vs RTNN |
| --- | ---: | ---: | ---: | ---: | ---: |
| 65,536 points, radius 0.02, K=50 | 0.877464 | 0.683743 | 1.283x faster | 1.357491 | 1.986x faster |
| 262,144 points, radius 0.02, K=50 | 3.444224 | 2.922729 | 1.178x faster | 1.527938 | 0.523x |

The 262,144-point row is improved but still trails RTNN. That is the key design signal: RTDL has moved beyond all-pairs CUDA, but it still lacks RTNN's stronger partitioning/batching and prepared-neighbor runtime contract.

## Negative RT Probe

A simple custom-primitive RT traversal was also tested. It was correct on the small Goal311 unit test, but it was not a performance win on the large synthetic rows:

| Input | Simple RT sec | Result |
| --- | ---: | --- |
| 65,536 points, radius 0.02, K=50 | 2.694051 | slower than old CUDA and uniform-cell |
| 262,144 points, radius 0.02, K=50 | 10.608099 | slower and not accepted as default |

This proves that "use OptiX" is not enough. The useful RTNN lesson is spatial organization plus prepared bounded search, not a naked ray traversal.

## Claim Boundary

This goal authorizes:

- a narrow claim that the RTDL OptiX backend now has a generic uniform-cell 3D bounded-neighbor path;
- a narrow claim that this path improves the current RTDL warm/raw rows by 1.28x at 65k and 1.18x at 262k on the tested RTX A5000 synthetic rows;
- a narrow claim that RTDL beats the collected RTNN warm row at 65k under this raw-row protocol.

This goal does not authorize:

- a broad RT-core speedup claim;
- a claim that the default path is RT-core accelerated;
- a claim that RTDL has reproduced RTNN;
- a claim that RTDL beats RTNN at 262k;
- a v2.2 release claim.

## Next Work

The next generic v2.2 primitive should be explicit prepared bounded neighbor search:

```text
prepared_bounded_neighbor_search_3d
```

Required additions:

- reusable prepared search-point grid or RT structure;
- batch/partition policy exposed in the execution plan;
- raw/device-resident row continuation so large neighbor streams do not require Python dict materialization;
- phase telemetry for pack, prepare, launch, copy, and normalization;
- exact/approx policy and overflow telemetry.

That remains v2.x runtime work, not v3.0 user-defined shader injection.
