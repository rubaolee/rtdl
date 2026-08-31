#!/usr/bin/env bash
set -euo pipefail

# Goal3975 helper for an already-running NVIDIA RTX Linux pod.
# Boundary: prepares local partner tooling only; does not create cloud resources
# and does not authorize release or performance claims.

INSTALL=1
SMOKE=1

while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-install)
      INSTALL=0
      ;;
    --no-smoke)
      SMOKE=0
      ;;
    --help)
      cat <<'EOF'
Usage: bash scripts/goal3975_current_scale_partner_pod_setup.sh [--skip-install] [--no-smoke]

Installs/pins the current scale-profile partner stack for driver-550 pods:
  numba==0.60.0
  numpy==2.0.2
  nvidia-cuda-nvcc-cu12==12.4.131
  cupy-cuda12x==14.1.1

Then prints the CUDA/Numba/RTDL environment exports needed before running
scripts/goal3828_current_benchmark_scale_profile_runner.py.
EOF
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
  shift
done

if [ "${INSTALL}" -eq 1 ]; then
  python3 -m pip install --break-system-packages --no-input \
    'numba==0.60.0' \
    'numpy==2.0.2' \
    'nvidia-cuda-nvcc-cu12==12.4.131' \
    'cupy-cuda12x==14.1.1'
fi

RTDL_CUDA_PREFIX="${RTDL_CUDA_PREFIX:-/usr/local/cuda-12}"
if [ ! -x "${RTDL_CUDA_PREFIX}/bin/nvcc" ]; then
  RTDL_CUDA_PREFIX="/usr/local/cuda"
fi

NUMBA_CUDA_PREFIX="${NUMBA_CUDA_PREFIX:-$(python3 - <<'PY'
import pathlib
import site

for raw_root in site.getsitepackages() + [site.getusersitepackages()]:
    root = pathlib.Path(raw_root)
    candidate = root / "nvidia" / "cuda_nvcc"
    if (candidate / "nvvm" / "lib64" / "libnvvm.so").exists():
        print(candidate)
        raise SystemExit(0)
raise SystemExit("unable to locate pip CUDA nvcc package root containing nvidia/cuda_nvcc")
PY
)}"

export RTDL_CUDA_PREFIX
export NUMBA_CUDA_PREFIX
export CUDA_HOME="${NUMBA_CUDA_PREFIX}"
export PATH="${NUMBA_CUDA_PREFIX}/bin:${RTDL_CUDA_PREFIX}/bin:${PATH}"
export LD_LIBRARY_PATH="${NUMBA_CUDA_PREFIX}/nvvm/lib64:${RTDL_CUDA_PREFIX}/targets/x86_64-linux/lib:${RTDL_CUDA_PREFIX}/lib64:${LD_LIBRARY_PATH:-}"

if [ "${SMOKE}" -eq 1 ]; then
  python3 - <<'PY'
import cupy as cp
from numba import cuda
import numpy as np


@cuda.jit
def add1(values):
    index = cuda.grid(1)
    if index < values.size:
        values[index] += 1


device = cuda.to_device(np.arange(8, dtype=np.int32))
add1[1, 32](device)
assert device.copy_to_host().tolist() == [1, 2, 3, 4, 5, 6, 7, 8]
assert int(cp.sum(cp.arange(8, dtype=cp.int32)).get()) == 28
print("partner_smoke_ok")
PY
fi

cat <<EOF
export RTDL_CUDA_PREFIX="${RTDL_CUDA_PREFIX}"
export NUMBA_CUDA_PREFIX="${NUMBA_CUDA_PREFIX}"
export CUDA_HOME="${NUMBA_CUDA_PREFIX}"
export PATH="${NUMBA_CUDA_PREFIX}/bin:${RTDL_CUDA_PREFIX}/bin:\$PATH"
export LD_LIBRARY_PATH="${NUMBA_CUDA_PREFIX}/nvvm/lib64:${RTDL_CUDA_PREFIX}/targets/x86_64-linux/lib:${RTDL_CUDA_PREFIX}/lib64:\${LD_LIBRARY_PATH:-}"
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY="\$PWD/build/librtdl_optix.so"
export RTDL_OPTIX_LIB="\$PWD/build/librtdl_optix.so"
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_NVCC="${RTDL_CUDA_PREFIX}/bin/nvcc"
export RTDL_OPTIX_PTX_ARCH=compute_89
export RTDL_OPTIX_CUBIN_ARCH=sm_89
EOF
