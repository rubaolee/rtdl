#!/usr/bin/env bash
set -euo pipefail

# Goal1062 generated runner for an already-running RTX-class Linux pod.
# Boundary: does not create cloud resources and does not authorize speedup claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-9.0.0}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"

if [ -z "${RTDL_SOURCE_COMMIT}" ]; then
  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-grade artifacts." >&2
  exit 2
fi

mkdir -p docs/reports/goal1062_blocked_rtx_wording_rerun
echo "Goal1062 blocked RTX wording rerun"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
nvidia-smi

echo "Goal1062 complete. Copy back docs/reports/goal1062_blocked_rtx_wording_rerun before stopping the pod."
