#!/usr/bin/env bash
set -euo pipefail
source "${ART}/bench_env.sh"
cd "${REPO}"
activate_repo_venv
make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" CUDA_PREFIX="${CUDA_PREFIX}" CUDA_LIB="${CUDA_LIB}" NVCC="${RTDL_NVCC}"
ls -lh build/librtdl_optix.so
