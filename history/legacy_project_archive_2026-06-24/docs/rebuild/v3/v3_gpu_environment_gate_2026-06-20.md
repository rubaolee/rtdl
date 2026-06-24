# V3 GPU Python Environment Gate

Status: Phoenix V3 environment evidence, 2026-06-20.

This document records the pod environment required by the repaired V3 current
benchmark run. It exists because RayDB, Numba, CuPy, and Torch failures must be
treated as release gates, not hidden setup trivia.

Artifact:

```text
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_20260620_061058/summary.json
```

Script-backed artifact:

```text
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_script_20260620_062113/summary.json
```

Reusable checker:

```bash
PYTHONPATH=src:. python scripts/v3_gpu_python_env_gate.py --pretty
```

Use `--dry-run` on machines without the GPU stack to inspect the required
package names and environment variables without importing CUDA libraries.

Remote artifact:

```text
/root/rtdl_v3_rebuild_20260620/artifacts/v3_gpu_python_env_gate_20260620_061058/summary.json
/root/rtdl_v3_rebuild_20260620/artifacts/v3_gpu_python_env_gate_script_20260620_062113/summary.json
```

## Passing Checks

| Check | Status | Meaning |
| --- | --- | --- |
| `cupy_rawkernel` | pass | CuPy can compile and run a CUDA RawKernel on the pod GPU. |
| `torch_cuda` | pass | PyTorch sees CUDA and runs a CUDA tensor operation. |
| `numba_cuda_jit` | pass | Numba can JIT and run a CUDA kernel with the configured nvcc/libnvvm path. |

## Package Set

| Package | Version |
| --- | --- |
| `cupy-cuda12x` | `14.1.1` |
| `torch` | `2.6.0+cu124` |
| `numba` | `0.65.1` |
| `nvidia-cuda-nvcc-cu12` | `12.4.131` |
| `nvidia-cuda-nvrtc-cu12` | `12.9.86` |
| `nvidia-cuda-runtime-cu12` | `12.9.79` |

## Required Environment Variables

```text
NUMBA_CUDA_PREFIX=/root/rtdl_v3_rebuild_20260620/.venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
CUDA_HOME=$NUMBA_CUDA_PREFIX
CUDA_PATH=$NUMBA_CUDA_PREFIX
PATH=$NUMBA_CUDA_PREFIX/bin:$PATH
LD_LIBRARY_PATH=$NUMBA_CUDA_PREFIX/nvvm/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:/usr/local/cuda-12/lib64:$LD_LIBRARY_PATH
RTDL_OPTIX_LIBRARY=/root/rtdl_v3_rebuild_20260620/current/build/librtdl_optix.so
RTDL_EMBREE_LIBRARY=/root/rtdl_v3_rebuild_20260620/current/build/librtdl_embree.so
```

## Remaining Caveat

The smoke run still emits a warning that `cuda-bindings` was built for CUDA
major 13 while the driver supports CUDA 12. The checks and repaired benchmark
rows pass, but V3 setup docs should keep this visible until the dependency set
is made quieter.

## Release Rule

No public V3 tutorial may rely on RayDB partner-resident rows or Numba rows
unless it also documents and verifies this gate.
