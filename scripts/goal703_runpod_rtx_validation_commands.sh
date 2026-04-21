#!/usr/bin/env bash
set -euo pipefail

# Goal703 RunPod helper.
# Run this inside an already-created RunPod Pod. It does not create cloud
# resources, does not contain credentials, and does not manage billing.

REPO_URL="${REPO_URL:-https://github.com/rubaolee/rtdl.git}"
CHECKOUT_DIR="${CHECKOUT_DIR:-$HOME/rtdl_runpod_validation}"
OPTIX_PREFIX="${OPTIX_PREFIX:-$HOME/vendor/optix-dev}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
COPIES="${COPIES:-128}"
ITERATIONS="${ITERATIONS:-5}"
RUNPOD_INSTALL_PACKAGES="${RUNPOD_INSTALL_PACKAGES:-1}"

echo "Goal703 RunPod RTDL RTX validation bootstrap"
echo "checkout_dir=${CHECKOUT_DIR}"
echo "optix_prefix=${OPTIX_PREFIX}"
echo "cuda_prefix=${CUDA_PREFIX}"
echo "nvcc=${NVCC}"
echo

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi is missing. Use a RunPod NVIDIA CUDA development template with GPU access." >&2
  exit 2
fi

nvidia-smi

if [ ! -x "${NVCC}" ]; then
  echo "nvcc is missing at ${NVCC}." >&2
  echo "Use a CUDA devel image or set CUDA_PREFIX/NVCC to the installed CUDA toolkit path." >&2
  exit 2
fi

"${NVCC}" --version

if [ "${RUNPOD_INSTALL_PACKAGES}" = "1" ] && command -v apt-get >/dev/null 2>&1 && [ "$(id -u)" = "0" ]; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libc6-dev-i386 \
    libgeos-dev \
    pkg-config
fi

if [ ! -f "${OPTIX_PREFIX}/include/optix.h" ]; then
  cat >&2 <<EOF
OptiX SDK header missing at:
  ${OPTIX_PREFIX}/include/optix.h

RunPod CUDA images normally include CUDA/driver support but may not include
NVIDIA OptiX SDK headers. Extract the OptiX SDK into ${OPTIX_PREFIX}, or set
OPTIX_PREFIX to the extracted SDK root, then rerun this script.
EOF
  exit 2
fi

if [ ! -d "${CHECKOUT_DIR}/.git" ]; then
  git clone "${REPO_URL}" "${CHECKOUT_DIR}"
fi

cd "${CHECKOUT_DIR}"
git fetch origin main --tags
git checkout main
git pull --ff-only origin main

chmod +x scripts/goal698_rtx_cloud_validation_commands.sh

OPTIX_PREFIX="${OPTIX_PREFIX}" \
CUDA_PREFIX="${CUDA_PREFIX}" \
NVCC="${NVCC}" \
RTDL_NVCC="${NVCC}" \
RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}" \
COPIES="${COPIES}" \
ITERATIONS="${ITERATIONS}" \
scripts/goal698_rtx_cloud_validation_commands.sh

python3 scripts/goal699_rtx_profile_report.py \
  --profile-json "docs/reports/goal698_rtx_cloud_fixed_radius_phase_profile_$(date +%Y-%m-%d).json" \
  --environment "docs/reports/goal698_rtx_cloud_environment_$(date +%Y-%m-%d).txt" \
  --output "docs/reports/goal703_runpod_rtx_profile_report_$(date +%Y-%m-%d).md"

echo
echo "Goal703 RunPod validation complete."
echo "Copy back docs/reports/goal698_rtx_cloud_environment_$(date +%Y-%m-%d).txt"
echo "Copy back docs/reports/goal698_rtx_cloud_fixed_radius_phase_profile_$(date +%Y-%m-%d).json"
echo "Copy back docs/reports/goal703_runpod_rtx_profile_report_$(date +%Y-%m-%d).md"
