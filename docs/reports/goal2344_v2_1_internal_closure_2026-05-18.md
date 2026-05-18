# Goal2344: Internal v2.1 Closure

Date: 2026-05-18

Status: internal checkpoint closed; not released

## Purpose

This goal closes the v2.1 work as an internal version. It does not publish a
release, create a package-install claim, or replace the v2.0 learner surface.
The goal is narrower:

1. Keep learner-facing docs clean and single-surface: v2.0 remains the current
   release.
2. Record v2.1 as internal research/audit evidence for RayJoin-style first-hit,
   Hausdorff tuning, and all-app rethink work.
3. Check that tutorial/example programs are ready to run locally and on the
   still-available RTX pod before the pod is shut down.

## What v2.1 Contains

| Area | Internal v2.1 result | Public boundary |
| --- | --- | --- |
| RayJoin-style spatial join | Generic prepared segment first-hit / nearest-boundary support improves the same-contract RayJoin PIP route from v2.0 by up to 72.93x in Goal2337 evidence. | Does not claim RTDL beats RayJoin or reproduces the full paper. |
| Hausdorff/X-HD-style benchmark | Scale-aware grouped point traversal defaults and pod runner are ready; prior RTX evidence remains strong up to 13.93x over grouped CuPy. | Fresh current-main pod timing is still needed before replacing prior public performance numbers. |
| All ordinary apps | Goal2342 rechecked every app; no ordinary app should be rewritten merely to use first-hit or Hausdorff tuning because that would change output contracts. | v2.0 app implementations remain the current learner versions. |
| Docs/examples | Public docs identify v2.1 as an internal checkpoint and point researchers/auditors to this report. | Normal learners should still start from v2.0 docs and examples. |

## Local Readiness Sweep

Local Windows source-tree commands used `PYTHONPATH=src;.` and the portable
CPU-reference or CPU-fallback command shapes.

| Scope | Result | Notes |
| --- | ---: | --- |
| Curated local tutorial/example commands | 35 pass / 37 run | Getting-started, feature, ordinary app, partner CPU-fallback, and research CPU-reference paths passed. |
| Local misses | 2 | `rtdl_hausdorff_v2_function.py --method openmp_cpu` and `rtdl_hausdorff_v2_user_benchmark.py` intentionally require a Linux/macOS OpenMP baseline. |
| Resolution | passed on pod | The same two Hausdorff research commands passed on the Linux RTX pod. |

The local artifact is kept in `scratch/goal2344_local_example_readiness.json`
because it includes the two expected platform-specific failures and is not a
release evidence artifact.

## Pod Readiness Sweep

Pod target:

```text
ssh root@69.30.85.175 -p 22114 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Hardware and runtime:

| Item | Value |
| --- | --- |
| GPU | NVIDIA RTX A5000 |
| Driver | 570.211.01 |
| Repo path | `/root/rtdl` |
| Commit | `1e9c9e72916ada21a2f223286f05b78f41f9eb9a` |
| Python | 3.12.3 |
| CUDA used for OptiX build | `/usr/local/cuda-12`, nvcc 12.8.93 |
| OptiX SDK | `/root/vendor/optix-sdk` |
| Embree package | Ubuntu `libembree-dev` 4.3.0 |
| CuPy | `cupy-cuda12x` 14.0.1 |

Build/setup actions:

```text
apt-get update -y
apt-get install -y libembree-dev
python3 -m pip install --break-system-packages --quiet cupy-cuda12x
make build-embree
CUDA_HOME=/usr/local/cuda-12 PATH=/usr/local/cuda-12/bin:$PATH \
  LD_LIBRARY_PATH=/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:/usr/local/cuda-12/compat:$LD_LIBRARY_PATH \
  make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12
```

OptiX linkage check:

```text
build/librtdl_optix.so -> libnvrtc.so.12
```

Result artifact:

`docs/reports/goal2344_v2_1_internal_closure_pod_example_readiness_2026-05-18.json`

| Scope | Commands | Result |
| --- | ---: | --- |
| Embree tutorial/feature/app/benchmark paths | 30 | 30 pass |
| OptiX/CuPy tutorial/feature/app/benchmark paths | 21 | 21 pass |
| Total pod readiness sweep | 51 | 51 pass |

The pod sweep includes:

- getting-started backend selection;
- database, graph, neighbor, ray-query, and spatial feature examples;
- ordinary analytics, geospatial, ML, robotics, simulation, and trajectory app
  examples;
- NumPy/Embree and CuPy/OptiX partner examples;
- Hausdorff research commands including the Linux OpenMP baseline;
- RayJoin-style Embree generic and OptiX prepared PIP paths.

## Documentation Operations

| File | Operation |
| --- | --- |
| `README.md` | Added a short internal-v2.1 note while preserving v2.0 as the released learner surface. |
| `docs/README.md` | Added internal status and linked this closure report from the docs index. |
| `docs/research/README.md` | Added this report as the research entry point for internal v2.1. |
| `docs/audit/README.md` | Added this report as the audit entry point for internal v2.1 closure evidence. |
| `examples/README.md` | Clarified that internal v2.1 does not create a new learner example tree. |
| `examples/v2_0/README.md` | Clarified that v2.1 keeps using the v2.0 learner tree. |
| `docs/reports/goal2344_v2_1_internal_closure_pod_example_readiness_2026-05-18.json` | Added pod readiness evidence for 51 Embree/OptiX commands. |

## Closeout Decision

Internal v2.1 can be closed as an engineering checkpoint.

Do not call it a release. Do not move tags. Do not advertise package-install
support. Do not claim broad RT-core speedup or that all user programs are
accelerated.

The correct public sentence is:

```text
RTDL v2.0 remains the current release; v2.1 is an internal checkpoint with
RayJoin/Hausdorff research improvements and 51-command Embree/OptiX example
readiness evidence.
```

## Validation

Validated locally:

```text
35/37 curated Windows source-tree tutorial/example commands passed.
The 2 platform-specific Hausdorff OpenMP commands passed on the Linux RTX pod.
```

Validated on pod:

```text
51/51 Embree and OptiX tutorial/example/benchmark commands passed.
```

Final verdict: `accept-with-boundary`.

Boundary: internal checkpoint only; public release remains blocked on a separate
release decision and the required consensus process.

## External Review

Goal2345 Gemini review was received with verdict `accept-with-boundary`.
Gemini verified that the report marks v2.1 as internal and not released, the
pod artifact supports the 51/51 result, public docs preserve v2.0 as the
learner/release surface, and claim boundaries remain intact.
