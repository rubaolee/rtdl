#!/usr/bin/env bash
set -euo pipefail
source "${ART}/bench_env.sh"
cd "${REPO}"
python3 -m venv .venv_bench
source .venv_bench/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install \
  'numpy==1.26.4' \
  'numba==0.60.0' \
  'nvidia-cuda-nvcc-cu12==12.4.131' \
  'cupy-cuda12x==13.6.0' \
  shapely pandas scipy networkx psutil pytest
python -m pip install -e .
activate_repo_venv
python - <<'PY'
import numpy as np
import rtdsl as rt
print("numpy", np.__version__)
print("embree", ".".join(map(str, rt.embree_version())))
import cupy as cp
print("cupy", cp.__version__, int(cp.sum(cp.arange(8, dtype=cp.int32)).get()))
from numba import cuda
@cuda.jit
def add1(x):
    i = cuda.grid(1)
    if i < x.size:
        x[i] += 1
d = cuda.to_device(np.arange(8, dtype=np.int32))
add1[1, 32](d)
print("numba", d.copy_to_host().tolist())
PY
