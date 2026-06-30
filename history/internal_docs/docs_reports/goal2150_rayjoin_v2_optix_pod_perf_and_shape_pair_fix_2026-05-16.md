# Goal2150 RayJoin v2 OptiX Pod Performance And Shape-Pair Compile Fix

Date: 2026-05-16

Status: pod evidence collected; external review pending.

## Purpose

Goal2145 added a RayJoin-style RTDL v2 user app. Goal2147 added a deterministic scale/perf harness. Goal2150 uses an NVIDIA pod to run the harness on CPU, Embree, and OptiX, and fixes a generated OptiX shape-pair kernel compile bug exposed by the overlay path.

This is a performance-development report, not a release claim.

## Pod Environment

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Environment artifact:

- `docs/reports/goal2150_rayjoin_v2_pod_environment_2026-05-16.txt`

Key environment facts:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- RTDL commit on pod: `b05c07df0c1e08d7babf3b17fdee85febffb711f`
- OptiX library: `/root/rtdl_rayjoin_pod/build/librtdl_optix.so`
- Generated PTX path: `RTDL_OPTIX_PTX_COMPILER=nvcc`, `RTDL_OPTIX_PTX_ARCH=compute_89`
- Embree: Ubuntu `libembree-dev`, `RTDL_EMBREE_PREFIX=/usr`
- GEOS: Ubuntu `libgeos-dev`, required by `run_cpu(...)`

## Setup Repairs

The pod initially needed three setup repairs:

1. `~/.ssh/id_ed25519` was rejected by the pod. The repo working key `id_ed25519_rtdl_codex` authenticated successfully.
2. The pod had CUDA and `libnvoptix`, but not GEOS/Embree development packages. Installed `libgeos-dev`, `pkg-config`, and `libembree-dev`.
3. The first generated overlay OptiX attempt failed under NVRTC due host math headers on this Ubuntu/CUDA combination. Retrying with the nvcc PTX path exposed the real kernel typo described below.

## App-Agnostic OptiX Fix

The overlay/shape-pair OptiX generated kernel declared:

```cpp
bool segment_intersection_hit = false;
```

but then wrote and read:

```cpp
segment_pair_intersection_hit
```

That caused nvcc PTX compilation to fail for `shape_pair_relation_kernel.cu`. Goal2150 fixes the variable declaration in `src/native/optix/rtdl_optix_core.cpp` to:

```cpp
bool segment_pair_intersection_hit = false;
```

This is not RayJoin app customization. It is an app-agnostic generated-kernel correctness fix for generic shape-pair relation traversal.

Guard test:

- `tests/goal2150_optix_shape_pair_relation_kernel_compile_test.py`

Validated locally:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2150_optix_shape_pair_relation_kernel_compile_test tests.goal2147_rayjoin_v2_scale_perf_test
```

Validated on pod by rebuilding `build/librtdl_optix.so` and rerunning the medium RayJoin harness.

## Pod Artifacts

Collected artifacts:

- `docs/reports/goal2150_rayjoin_v2_scale_perf_medium_pod_2026-05-16.json`
- `docs/reports/goal2150_rayjoin_v2_scale_perf_large_pip_lsi_pod_2026-05-16.json`
- `docs/reports/goal2150_rayjoin_v2_pod_environment_2026-05-16.txt`

Medium command:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_rayjoin_pod/build/librtdl_optix.so RTDL_EMBREE_PREFIX=/usr \
RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/local/cuda-12.8/bin/nvcc RTDL_NVCC_CCBIN=/usr/bin/g++ RTDL_OPTIX_PTX_ARCH=compute_89 \
python3 scripts/goal2147_rayjoin_v2_scale_perf.py --scale medium --backends cpu,embree,optix --repeats 3 --warmups 1 \
  --output docs/reports/goal2150_rayjoin_v2_scale_perf_medium_pod_2026-05-16.json
```

Large PIP/LSI command:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_rayjoin_pod/build/librtdl_optix.so RTDL_EMBREE_PREFIX=/usr \
RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/local/cuda-12.8/bin/nvcc RTDL_NVCC_CCBIN=/usr/bin/g++ RTDL_OPTIX_PTX_ARCH=compute_89 \
python3 scripts/goal2147_rayjoin_v2_scale_perf.py --scale large --workloads pip,lsi --backends cpu,embree,optix --repeats 3 --warmups 1 \
  --output docs/reports/goal2150_rayjoin_v2_scale_perf_large_pip_lsi_pod_2026-05-16.json
```

## Medium Results

All medium rows preserved parity against CPU Python reference.

| Workload | Inputs | Rows | CPU median sec | Embree median sec | OptiX median sec | OptiX vs CPU | OptiX vs Embree |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pip` | 1,024 points / 256 polygons | 1,024 | 0.003706 | 0.003642 | 0.002488 | 1.49x | 1.46x |
| `lsi` | 128 left / 128 right segments | 16,384 | 0.022420 | 0.026350 | 0.016080 | 1.39x | 1.64x |
| `overlay_seed` | 128 left / 128 right polygons | 16,384 pair rows / 128 active seeds | 0.202004 | 0.015115 | 0.019069 | 10.59x | 0.79x |

Medium interpretation:

- OptiX wins PIP and LSI.
- OptiX overlay is correct and much faster than CPU, but Embree is faster at this size.
- Overlay reference generation is slow because the CPU Python truth path is intentionally simple; this reinforces why warmups/progress logs are required.

## Large PIP/LSI Results

Large overlay was deliberately not run because its Python truth path scales too slowly for the current harness. Large PIP and LSI preserved parity.

| Workload | Inputs | Rows | CPU median sec | Embree median sec | OptiX median sec | OptiX vs CPU | OptiX vs Embree |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pip` | 4,096 points / 1,024 polygons | 4,096 | 0.018510 | 0.005658 | 0.014360 | 1.29x | 0.39x |
| `lsi` | 256 left / 256 right segments | 65,536 | 0.093596 | 0.071418 | 0.065615 | 1.43x | 1.09x |

Large interpretation:

- OptiX still wins dense LSI, though the win over Embree is modest at this scale.
- Large disjoint PIP does not favor OptiX on this synthetic layout; Embree is 2.54x faster than OptiX. This likely reflects a combination of compact CPU-side Embree traversal, low per-query work after pruning, and OptiX launch/transfer/finalization overhead.
- This is a useful result, not a failure: RTDL v2 is exposing where RT cores help and where CPU RT traversal remains a better backend.

## What This Says About The Upcoming RayJoin Fight

Current prediction after pod evidence:

1. LSI is promising for OptiX, especially as row counts grow, but dense all-crossing synthetic cases cap the upside because every pair becomes a hit.
2. PIP needs dataset-shape care. Sparse positive-hit rows are correct, but disjoint simple squares can favor Embree. More RayJoin-like polygon complexity may shift the fight.
3. Overlay has a correct OptiX path after Goal2150, but the current medium result favors Embree. Full overlay remains a continuation/topology problem, not just a traversal problem.
4. The next serious step is not another tiny smoke. It is RayJoin-repository/public dataset ingestion plus CUDA/CuPy non-RT baselines on the same inputs.

## Claim Boundary

This goal authorizes:

- OptiX execution evidence for the RTDL v2 RayJoin harness on one RTX 4000 Ada pod.
- CPU/Embree/OptiX parity evidence for the measured synthetic cases.
- A narrow statement that OptiX is faster than CPU and Embree on medium PIP/LSI, faster than CPU on measured medium overlay, and faster than CPU/Embree on large LSI.
- A narrow statement that Embree is faster than OptiX on measured large synthetic PIP and medium overlay.

This goal does not authorize:

- full RayJoin paper reproduction
- paper-scale performance claims
- broad RT-core speedup claims
- whole-app polygon overlay acceleration claims
- v2.0 release authorization
- replacing the existing 3-AI release-consensus rule

The JSON artifacts intentionally keep `rt_core_speedup_claim_authorized` as `false`; that flag means "no broad/public RT-core speedup claim," not "OptiX did not execute."

## Next Work

1. Add RayJoin repository/public dataset adapters outside the native engine.
2. Run same-contract PIP/LSI tests on RayJoin-like public data.
3. Add CUDA/CuPy non-RT baselines for PIP and LSI.
4. Investigate whether large PIP loses to Embree because of launch overhead, host finalization, candidate density, or output transfer.
5. Decide whether v2 needs a generic point-location/closest-owner output contract for RayJoin-style PIP.
6. Seek external review before using this evidence in any public claim.

## Verdict

Goal2150 is accepted as pod performance-development evidence and as a required OptiX shape-pair compile fix. It is not a release gate closure.
