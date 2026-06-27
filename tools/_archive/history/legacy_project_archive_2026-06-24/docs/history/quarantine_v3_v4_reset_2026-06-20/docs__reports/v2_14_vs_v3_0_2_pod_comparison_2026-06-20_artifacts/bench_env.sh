set -euo pipefail
export OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0
export CUDA_PREFIX=/usr/local/cuda
export CUDA_LIB=/usr/local/cuda/targets/x86_64-linux/lib
export RTDL_CUDA_PREFIX=/usr/local/cuda
export RTDL_OPTIX_PTX_COMPILER=nvcc
export RTDL_NVCC=/usr/local/cuda/bin/nvcc
export RTDL_OPTIX_PTX_ARCH=compute_89
export RTDL_OPTIX_CUBIN_ARCH=sm_89
export PATH="/usr/local/cuda/bin:${PATH}"
export LD_LIBRARY_PATH="/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
export PYTHONPATH=src:.
activate_repo_venv() {
  source "${REPO}/.venv_bench/bin/activate"
  local site
  site=$(python - <<'PY'
import site
print(site.getsitepackages()[0])
PY
)
  export NUMBA_CUDA_PREFIX="${site}/nvidia/cuda_nvcc"
  export CUDA_HOME="${NUMBA_CUDA_PREFIX}"
  export CUDA_PATH=/usr/local/cuda
  export CUPY_CUDA_PATH=/usr/local/cuda
  export PATH="${NUMBA_CUDA_PREFIX}/bin:/usr/local/cuda/bin:${PATH}"
  export LD_LIBRARY_PATH="${NUMBA_CUDA_PREFIX}/nvvm/lib64:/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
  export RTDL_OPTIX_LIBRARY="${REPO}/build/librtdl_optix.so"
  export RTDL_OPTIX_LIB="${REPO}/build/librtdl_optix.so"
  export RTDL_EMBREE_LIBRARY="${REPO}/build/librtdl_embree.so"
}
