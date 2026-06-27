# GPU Partner Gate

Status: V3 rebuild tutorial.

Some V3 routes use explicit Python GPU partners. That is allowed only when the
environment gate passes.

Current pod gate:

| Check | Status |
| --- | --- |
| CuPy RawKernel | pass |
| Torch CUDA tensor | pass |
| Numba CUDA JIT | pass |

Required package set from the pod:

| Package | Version |
| --- | --- |
| `cupy-cuda12x` | `14.1.1` |
| `torch` | `2.6.0+cu124` |
| `numba` | `0.65.1` |
| `nvidia-cuda-nvcc-cu12` | `12.4.131` |
| `nvidia-cuda-nvrtc-cu12` | `12.9.86` |
| `nvidia-cuda-runtime-cu12` | `12.9.79` |

The environment evidence is:

```text
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_20260620_061058/summary.json
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_script_20260620_062113/summary.json
```

Reusable checker:

```bash
PYTHONPATH=src:. python scripts/v3_gpu_python_env_gate.py --pretty
```

On a non-GPU machine, inspect the required package set without importing CUDA:

```powershell
py -3 scripts\v3_gpu_python_env_gate.py --dry-run --pretty
```

Public V3 setup docs must reproduce this gate before teaching RayDB
partner-resident rows or Numba continuation rows.

Read next:

- [Claim Boundaries](06_claim_boundaries.md)
