# Goal2120 Clean A5000 OptiX Hausdorff Rerun

Date: 2026-05-16

Status: evidence recorded.

## Purpose

This goal continues the interrupted Hausdorff Distance language-lab validation from Goal2119 on a fresh pod. The specific question was whether the previous OptiX module compiler failure was an unavoidable RTDL/Hausdorff problem or an environment-specific pod problem, and whether a clean reinstall/setup could make the RTDL/OptiX path execute.

The answer is:

- Clean pod setup succeeded.
- RTDL OptiX native controls passed.
- The RTDL/OptiX Hausdorff nearest-witness path compiles and returns exact values on this pod.
- The current RT-core Hausdorff formulation is not performance-competitive with the v2.0 user-level CuPy continuation.
- RT-core Hausdorff speedup claim remains `needs-more-evidence`.

## Pod And Setup

Pod command provided by the user:

```text
ssh root@69.30.85.189 -p 22108 -i ~/.ssh/id_ed25519
```

Actual key used by Codex per project rule:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\id_ed25519_rtdl_codex
```

Observed hardware and software:

| Field | Value |
| --- | --- |
| Host | `c90b15d45972` |
| GPU | `NVIDIA RTX A5000` |
| Driver | `570.211.01` |
| GPU memory | `24564 MiB` |
| OS | Ubuntu 24.04.3 |
| CUDA prefix | `/usr/local/cuda-12.8` |
| OptiX SDK | `/root/vendor/optix-sdk`, tag `v8.1.0` |
| Repo checkout | `/root/work/rtdl` |
| Repo commit | `3dc68e92` |

Install/repair steps performed:

```text
apt-get update
apt-get install -y git ca-certificates build-essential g++ make pkg-config libgeos-dev python3 python3-pip python3-venv cuda-nvcc-12-8 cuda-nvrtc-dev-12-8 cuda-cudart-dev-12-8 cuda-driver-dev-12-8
ln -sfn /usr/local/cuda-12.8 /usr/local/cuda
python3 -m pip install numpy cupy-cuda12x
git clone https://github.com/rubaolee/rtdl /root/work/rtdl
git clone https://github.com/NVIDIA/optix-sdk /root/vendor/optix-sdk
cd /root/vendor/optix-sdk && git checkout v8.1.0
cd /root/work/rtdl && make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8
```

The OptiX backend linked against the pod driver/CUDA stack:

```text
libcuda.so.1 => /usr/lib/x86_64-linux-gnu/libcuda.so.1
libnvrtc.so.12 => /usr/local/cuda-12.8/targets/x86_64-linux/lib/libnvrtc.so.12
```

## OptiX Controls

RTDL OptiX native controls passed.

The following native OptiX controls passed after setup:

```text
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/root/work/rtdl/build/librtdl_optix.so \
RTDL_OPTIX_PTX_COMPILER=nvcc \
RTDL_OPTIX_PTX_ARCH=compute_86 \
RTDL_NVCC=/usr/local/cuda-12.8/bin/nvcc \
RTDL_NVCC_CCBIN=/usr/bin/g++ \
python3 -m unittest \
  tests.goal637_optix_native_any_hit_test \
  tests.goal162_optix_visual_demo_parity_test
```

Result:

```text
Ran 4 tests in 2.371s
OK
```

This proves the new pod can compile and execute RTDL custom OptiX modules. The Goal2119 compiler failure was therefore pod/environment-specific, not a universal RTDL/Hausdorff compiler failure.

## Hausdorff Methods Compared

The tested function computes exact directed Hausdorff distance for two point sets where the exact result is:

```text
max over source points of min squared/euclidean distance to target points
```

Methods:

| Method | Role | Uses RTDL | Uses partner | Uses RT cores | Exact |
| --- | --- | ---: | ---: | ---: | ---: |
| `openmp_cpu` | C++/OpenMP exact baseline | no | no | no | yes |
| `cuda_cpp` | standalone CUDA C++ tiled exact baseline | no | no | no | yes |
| `cupy_rawkernel` | CuPy exact RawKernel baseline | no | yes | no | yes |
| `rtdl_v2_user_cuda` | RTDL v2 user program: RTDL row/column orchestration plus CuPy exact continuation | yes | yes | no | yes |
| `rtdl_rt_threshold_search` | RTDL/OptiX fixed-radius decision search | yes | no | yes | tolerance interval only |
| `rtdl_rt_nearest_witness` | RTDL/OptiX nearest-witness traversal seeded by threshold-search upper bound | yes | no | yes | yes |
| `rtdl_rt_nearest_witness_oracle_radius` | Diagnostic RTDL/OptiX nearest-witness traversal using exact-reference radius plus slack | yes | no | yes | yes |

The oracle-radius rows are diagnostic lower bounds for the current RT nearest-witness path. They avoid threshold-search iterations by using the exact reference distance plus slack as the traversal radius. They are not deployable algorithms because the exact distance is already known.

## 512 Point Smoke Result

Artifact: `docs/reports/goal2120_new_pod_hd_smoke_512.json`

| Method | Seconds | Exact match | Notes |
| --- | ---: | ---: | --- |
| `openmp_cpu` | 0.100813 | yes | multi-thread CPU exact baseline |
| `cuda_cpp` | 0.001771 | yes | standalone CUDA exact baseline |
| `cupy_rawkernel` | 0.000857 | yes | CuPy exact continuation |
| `rtdl_v2_user_cuda` | 0.000806 | yes | RTDL v2 plus CuPy exact continuation |
| `rtdl_rt_threshold_search` | 0.568111 | no | interval only, tolerance `0.001` |
| `rtdl_rt_nearest_witness` | 0.410289 | yes | RT-core exact nearest witness |

At this size, `rtdl_v2_user_cuda` is about 125x faster than `openmp_cpu`, while the exact RT-core nearest-witness path is about 509x slower than `rtdl_v2_user_cuda`.

## Oracle-Radius Scale Diagnostic

Artifacts:

- `docs/reports/goal2120_new_pod_hd_oracle_radius_4096.json`
- `docs/reports/goal2120_new_pod_hd_oracle_radius_8192.json`
- `docs/reports/goal2120_new_pod_hd_oracle_radius_32768.json`
- `docs/reports/goal2120_new_pod_hd_oracle_radius_65536.json`

| Points A/B | `cuda_cpp` sec | `cupy_rawkernel` sec | `rtdl_v2_user_cuda` sec | RT oracle-radius sec | RT exact | RT / v2 user CUDA |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4,096 | 0.010573 | 0.004541 | 0.004556 | 0.832766 | yes | 182.77x slower |
| 8,192 | 0.009693 | 0.008863 | 0.008867 | 0.969555 | yes | 109.35x slower |
| 32,768 | 0.070446 | 0.069363 | 0.059924 | 1.541813 | yes | 25.73x slower |
| 65,536 | n/a | 0.239384 | 0.238662 | 2.336760 | yes | 9.79x slower |

Every RT oracle-radius run matched the exact reference value. However, even this favorable diagnostic path is slower than the user-level CuPy continuation.

## Interpretation

The clean pod changes the diagnosis from "compiler is blocked" to "algorithmic formulation is the blocker."

The current RTDL/OptiX Hausdorff path represents target points as fixed-radius AABBs and asks OptiX to find nearest witnesses by repeated or bounded traversal. That is real RT-core execution, but it is not yet an X-HD-style algorithm. It lacks:

- hierarchy-aware point-set pruning,
- heavy-cell scheduling,
- early rejection/acceptance over structured point clusters,
- reusable bounded candidate summarization for distance witnesses,
- a data-dependent plan that reduces enough distance work before launching RT traversal.

For dense point clouds, the GPU tiled/RawKernel continuation has excellent memory locality and much lower orchestration overhead. The current RT path pays BVH/custom-primitive traversal overhead without enough pruning to compensate.

## Release Boundary

Accepted claims:

- The A5000 pod can build and run RTDL OptiX native modules after clean dependency setup.
- RTDL v2 can express an exact Hausdorff user program using partner CuPy continuation.
- The exact v2 CuPy continuation is much faster than the OpenMP CPU baseline on the tested rows.
- The current RTDL/OptiX Hausdorff nearest-witness path returns exact values on the tested rows.

Blocked claims:

- Do not claim exact Hausdorff is RT-core accelerated for performance yet.
- Do not claim X-HD parity.
- Do not claim broad RT-core speedup from these results.
- Do not use `rtdl_rt_nearest_witness_oracle_radius` as a deployable algorithm, because it uses the exact reference radius.

Goal2120 verdict:

```text
RTDL v2 language correctness for exact Hausdorff: accept
Clean A5000 OptiX environment: accept
RT-core Hausdorff speedup: needs-more-evidence
X-HD-style algorithm readiness: needs-more-evidence
```

## Next Work

The next useful work is not another reinstall. The environment is now proven good.

The design task is to implement an X-HD-inspired RTDL v2 Hausdorff application or a new reusable generic primitive that can express:

- hierarchy or grid cells over point sets,
- bounded candidate/witness streaming,
- per-cell lower/upper distance bounds,
- partner-side reduction over candidates,
- exact final witness extraction.

That work must stay app-agnostic at the engine layer. App-specific Hausdorff planning belongs in Python/partner code over generic RTDL primitives unless a new primitive is justified, reviewed, and named generically.
