#!/usr/bin/env bash
set -euo pipefail

# Goal698 helper for a fresh RTX-class Linux VM.
# Run from the root of an RTDL checkout after CUDA/NVIDIA driver and OptiX SDK
# headers are present. This script does not create cloud resources and does not
# contain credentials.

COPIES="${COPIES:-128}"
ITERATIONS="${ITERATIONS:-5}"
OPTIX_PREFIX="${OPTIX_PREFIX:-$HOME/vendor/optix-dev}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr}"
NVCC="${NVCC:-/usr/bin/nvcc}"
REPORT_DIR="${REPORT_DIR:-docs/reports}"
DATE_TAG="${DATE_TAG:-$(date +%Y-%m-%d)}"
JSON_OUT="${REPORT_DIR}/goal698_rtx_cloud_fixed_radius_phase_profile_${DATE_TAG}.json"
TXT_OUT="${REPORT_DIR}/goal698_rtx_cloud_environment_${DATE_TAG}.txt"

mkdir -p "${REPORT_DIR}"

{
  echo "Goal698 RTDL RTX cloud validation environment"
  echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "repo=$(pwd)"
  echo "commit=$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
  echo "python=$(python3 --version 2>&1)"
  echo "optix_prefix=${OPTIX_PREFIX}"
  echo "cuda_prefix=${CUDA_PREFIX}"
  echo "nvcc=${NVCC}"
  echo
  echo "nvidia-smi:"
  nvidia-smi || true
  echo
  echo "nvcc version:"
  "${NVCC}" --version || true
} | tee "${TXT_OUT}"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi not found; install or use an NVIDIA GPU image before running this script." >&2
  exit 2
fi

if [ ! -x "${NVCC}" ]; then
  echo "nvcc not found or not executable at ${NVCC}; set NVCC=/path/to/nvcc." >&2
  exit 2
fi

if [ ! -f "${OPTIX_PREFIX}/include/optix.h" ]; then
  echo "OptiX SDK header missing at ${OPTIX_PREFIX}/include/optix.h." >&2
  echo "Install/extract NVIDIA OptiX SDK and set OPTIX_PREFIX to its root." >&2
  exit 2
fi

python3 -m pip install --user --upgrade pip >/dev/null

make build-optix \
  OPTIX_PREFIX="${OPTIX_PREFIX}" \
  CUDA_PREFIX="${CUDA_PREFIX}" \
  NVCC="${NVCC}"

export PYTHONPATH="src:."
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"

python3 - <<'PY'
import json
import rtdsl as rt

print(json.dumps({"optix_version": rt.optix_version(), "rtdl_optix_lib": __import__("os").environ["RTDL_OPTIX_LIB"]}, sort_keys=True))
PY

python3 -m unittest -v \
  tests.goal695_optix_fixed_radius_summary_test \
  tests.goal696_optix_fixed_radius_linux_validation_test \
  tests.goal697_optix_fixed_radius_phase_profiler_test \
  tests.goal216_fixed_radius_neighbors_optix_test \
  tests.goal690_optix_performance_classification_test

python3 scripts/goal697_optix_fixed_radius_phase_profiler.py \
  --mode optix \
  --copies "${COPIES}" \
  --iterations "${ITERATIONS}" \
  --output "${JSON_OUT}"

echo "Goal698 RTX cloud validation artifacts:"
echo "  ${TXT_OUT}"
echo "  ${JSON_OUT}"
