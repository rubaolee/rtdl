# Goal2117: Hausdorff v2 Pod Performance and X-HD Gap

Date: 2026-05-16

Status: evidence collected, release claim boundary preserved.

## Purpose

This goal stress-tests the RTDL v2.0 user model on a real Hausdorff Distance workload:

- write exact HD as `Python + partner + RTDL`;
- compare it against independent multi-threaded OpenMP CPU, standalone CUDA C++, and direct CuPy RawKernel baselines;
- attempt the RTDL/OptiX RT-core threshold and nearest-witness paths;
- state precisely what still separates this lab from an X-HD-class RT-accelerated Hausdorff implementation.

This is a language lab, not a v2.0 release authorization.

## Pod Environment

Command provided by the user:

```text
ssh root@213.173.102.150 -p 36295 -i ~/.ssh/id_ed25519
```

Codex used the project working key at:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\id_ed25519_rtdl_codex
```

Observed pod:

| Field | Value |
| --- | --- |
| Host | `c54d2d041030` |
| GPU | NVIDIA RTX 2000 Ada Generation |
| Driver | 565.57.01 |
| GPU memory | 16380 MiB |
| CUDA prefix | `/usr/local/cuda-12.8` |
| OptiX SDK attempted | `/root/vendor/optix-sdk`, v8.1.0 and v8.0.0 attempts |
| Repo | `/root/work/rtdl` |
| Commit at start | `d8196cc1` |

## Correctness and Performance Evidence

All successful rows compute exact undirected 2D Hausdorff distance. The `rtdl_v2_user_cuda` method is the v2.0 user path: RTDL/Python normalizes point rows into partner columns and a user-owned CuPy RawKernel continuation computes the exact directed reductions.

| Points A x B | OpenMP CPU sec | CUDA C++ sec | CuPy RawKernel sec | RTDL v2 user CUDA sec | RTDL matches exact | RTDL / CUDA C++ |
| ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 4,096 x 4,096 | 0.014076710 | 0.005910471 | 0.003661513 | 0.003644750 | yes | 0.617x |
| 8,192 x 8,192 | 0.016847365 | n/a | 0.013907246 | 0.013905734 | yes | n/a |
| 32,768 x 32,768 | 1.566554852 | 0.164027795 | 0.155364238 | 0.150213115 | yes | 0.916x |
| 65,536 x 65,536 | n/a | 0.585788377 | 0.582640566 | 0.582772970 | yes | 0.995x |
| 131,072 x 131,072 | n/a | 2.333903179 | 2.328677490 | 2.328834541 | yes | 0.998x |
| 262,144 x 262,144 | n/a | 9.132231191 | 9.121580981 | 9.121583052 | yes | 0.999x |

Interpretation:

- The v2.0 user path is exact and has effectively no overhead relative to direct CuPy RawKernel once the input is already expressed as partner columns.
- It is competitive with the standalone CUDA C++ baseline after the CUDA C++ baseline is compiled for the actual Ada architecture (`RTDL_HAUSDORFF_CUDA_ARCH=sm_89`).
- At 32,768 points per side, the exact RTDL v2 user path is about 10.43x faster than the OpenMP CPU baseline on this pod. Larger OpenMP rows were deliberately not run because the GPU baselines already establish the serious comparison and the CPU double loop becomes wasteful.

## CUDA C++ Baseline Repair

The first standalone CUDA C++ baseline returned a false distance of zero on this pod. Goal2117 hardened the user-level CUDA baseline so it no longer silently treats CUDA runtime failures as valid results:

- every CUDA allocation/copy/launch/sync/copy-back status is checked;
- failure returns a NaN sentinel and Python raises a runtime error;
- `RTDL_HAUSDORFF_CUDA_ARCH` can be set for the generated `nvcc` build.

The error-check artifact shows the old launch failure explicitly:

```text
CUDA C++ Hausdorff baseline failed: stage=12 cuda_status=222
```

Re-running with:

```text
NVCC=/usr/local/cuda-12.8/bin/nvcc
RTDL_HAUSDORFF_CUDA_ARCH=sm_89
```

produced exact matching CUDA C++ results at 4,096 through 262,144 points per side.

## RT-Core Attempt

The RTDL/OptiX paths were attempted after:

- installing/locating CUDA 12.8;
- installing CuPy;
- cloning OptiX SDK under `/root/vendor/optix-sdk`;
- trying OptiX SDK v8.1.0 and v8.0.0;
- building `librtdl_optix.so`;
- adding a host-count split for the fixed-radius count path to reduce the launch-parameter surface;
- trying a module optimization-level reduction on the pod.

The OptiX fixed-radius count module still fails before any useful HD RT timing:

```text
OptiX module compile error: Internal compiler error
entry function "__intersection__frn_count_host_isect"
entry function "__anyhit__frn_count_host_anyhit"
entry function "__raygen__frn_count_host_probe"
Pipeline parameter "params" size is 56 bytes
```

Therefore:

- no RT-core exact Hausdorff speedup claim is authorized by this pod;
- no X-HD parity claim is authorized;
- the RTDL exact HD result in this goal is a strong `Python + partner + RTDL` demonstration, not an RT-core HD win.

## Difference From X-HD After This Goal

The X-HD paper's acceleration is not merely "call OptiX for nearest neighbor." It combines spatial hierarchy, bounding logic, pruning, and selective heavy work. After Goal2117, RTDL has a useful exact v2 user implementation but still lacks the X-HD algorithmic layers:

| X-HD ingredient | Current RTDL v2 HD lab |
| --- | --- |
| Hierarchical grouping / cells / bounding boxes | Not implemented in the HD user app. |
| Estimator or bound-based candidate pruning | Not implemented beyond the failed fixed-radius RT decision attempt. |
| Early-break directed-distance logic | Not implemented. |
| Heavy-cell fallback between RT and CUDA | Not implemented. |
| Exact witness extraction at scale | Implemented for CUDA/CuPy exact path; RT witness path blocked on pod. |
| RT-core acceleration evidence | Blocked by OptiX module compiler ICE on this pod. |
| General v2 language value | Demonstrated: RTDL partner columns compose cleanly with user CUDA/CuPy code. |

Design insight:

RTDL v2.0 should not bake "Hausdorff" into the native engine. The general solution is to provide generic candidate/decision/witness tables and partner-column handoff so user programs can build X-HD-style algorithms outside the engine. The next HD-specific work should be an app-level X-HD-inspired user program over generic RTDL primitives plus partner kernels, not a native app customization.

## Artifacts

| Artifact | Purpose |
| --- | --- |
| `docs/reports/goal2117_pod_hd_cuda_cpp_errorcheck_512.json` | Captures the pre-arch CUDA C++ failure as explicit status instead of false zero. |
| `docs/reports/goal2117_pod_hd_cuda_cpp_sm89_4096.json` | Correct CUDA C++ / CuPy / RTDL comparison after `sm_89` fix. |
| `docs/reports/goal2117_pod_hd_cuda_cpp_sm89_32768.json` | Same-contract exact comparison at 32k. |
| `docs/reports/goal2117_pod_hd_cuda_cpp_sm89_65536.json` | Same-contract exact comparison at 65k. |
| `docs/reports/goal2117_pod_hd_cuda_cpp_sm89_131072.json` | Same-contract exact comparison at 131k. |
| `docs/reports/goal2117_pod_hd_cuda_cpp_sm89_262144.json` | Same-contract exact comparison at 262k. |
| `docs/reports/goal2117_pod_hd_nonrt_8192.json` | OpenMP / CuPy / RTDL comparison at 8k. |
| `docs/reports/goal2117_pod_hd_nonrt_32768.json` | OpenMP / CuPy / RTDL comparison at 32k. |
| `docs/reports/goal2117_pod_hd_nonrt_65536.json` | CuPy / RTDL comparison at 65k. |
| `docs/reports/goal2117_pod_hd_nonrt_131072.json` | CuPy / RTDL comparison at 131k. |
| `docs/reports/goal2117_pod_hd_nonrt_262144.json` | CuPy / RTDL comparison at 262k. |
| `docs/reports/goal2117_pod_hd_smoke_512_host_count_split.json` | RTDL/OptiX attempt showing the fixed-radius module compiler blocker. |

## Verdict

- Exact RTDL v2 user HD path: `accept`.
- Standalone CUDA C++ baseline: `accept` after explicit `sm_89` compile and error checking.
- RT-core HD claim: `needs-more-evidence`.
- X-HD parity claim: `needs-more-evidence`.
- v2.0 release relevance: this is valuable user-language evidence, but it is not a release button.
