#!/usr/bin/env bash
set -euo pipefail

# Goal1194 pod-side executor for the reviewed Goal1192/Goal1193 public-wording
# evidence batch. Run on an RTX-class Linux pod after uploading the source
# archive. This script produces artifacts only; it does not authorize public
# speedup wording.

ARCHIVE="${ARCHIVE:-/tmp/goal1194_rtdl_source_2026-04-30.tar.gz}"
EXPECTED_SHA256="${EXPECTED_SHA256:-}"
WORKDIR="${WORKDIR:-/workspace/rtdl_goal1194}"
SOURCE_DIR="${WORKDIR}/rtdl_staged_source"
RESULT_DIR="${RESULT_DIR:-docs/reports/goal1192_public_wording_evidence_batch}"
RESULT_TGZ="${RESULT_TGZ:-/tmp/goal1194_goal1192_public_wording_evidence_batch.tgz}"
RESULT_SHA="${RESULT_SHA:-/tmp/goal1194_goal1192_public_wording_evidence_batch.tgz.sha256}"

echo "Goal1194 public wording evidence pod executor"
echo "archive=${ARCHIVE}"
echo "expected_sha256=${EXPECTED_SHA256}"
echo "workdir=${WORKDIR}"
echo "result_dir=${RESULT_DIR}"

if [ -z "${EXPECTED_SHA256}" ]; then
  echo "EXPECTED_SHA256 must be set." >&2
  exit 2
fi

if [ ! -f "${ARCHIVE}" ]; then
  echo "Archive not found: ${ARCHIVE}" >&2
  exit 2
fi

actual_sha256="$(sha256sum "${ARCHIVE}" | awk '{print $1}')"
echo "actual_sha256=${actual_sha256}"
if [ "${actual_sha256}" != "${EXPECTED_SHA256}" ]; then
  echo "Archive SHA256 mismatch." >&2
  exit 2
fi

rm -rf "${WORKDIR}"
mkdir -p "${WORKDIR}"
tar -xzf "${ARCHIVE}" -C "${WORKDIR}"
cd "${SOURCE_DIR}"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y build-essential git cmake pkg-config libgeos-dev libembree-dev python3-dev python3-pip

# CUDA dev packages are image-specific. Try the CUDA 13 names used by recent
# pods, but do not fail if the base image already provides the CUDA toolchain.
# `make build-optix` invokes nvcc directly, so the nvcc package is mandatory
# when the base image only ships the driver/runtime.
apt-get install -y cuda-nvcc-13-0 cuda-nvrtc-dev-13-0 cuda-cudart-dev-13-0 || true

cat > .gitignore <<'EOF'
__pycache__/
*.pyc
*.pyo
*.o
*.a
*.so
*.dylib
build/
dist/
out/
docs/reports/
EOF

git init
git config user.email "pod@example.com"
git config user.name "RTDL Pod"
git add .
git commit -m "Goal1194 staged source archive"

export RTDL_SOURCE_COMMIT="goal1194-archive-${EXPECTED_SHA256}"
export PYTHONPATH="${PYTHONPATH:-src:.}"

mkdir -p "${RESULT_DIR}"
{
  echo "Goal1194 environment"
  date -u
  uname -a
  nvidia-smi || true
  python3 --version || true
  which nvcc || true
  nvcc --version || true
  sha256sum "${ARCHIVE}"
  echo "rtdl_source_commit=${RTDL_SOURCE_COMMIT}"
  git rev-parse HEAD
  git status --short
} | tee "${RESULT_DIR}/goal1194_environment.log"

mkdir -p /root/vendor
if [ ! -d /root/vendor/optix-dev ]; then
  git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-dev.git /root/vendor/optix-dev
fi

export OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-dev}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"

make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" CUDA_PREFIX="${CUDA_PREFIX}" NVCC="${NVCC}" \
  2>&1 | tee "${RESULT_DIR}/make_build_optix.log"

OUTDIR="${RESULT_DIR}" bash scripts/goal1192_public_wording_evidence_batch_runner.sh \
  2>&1 | tee "${RESULT_DIR}/goal1192_runner.log"

tar -czf "${RESULT_TGZ}" "${RESULT_DIR}"
sha256sum "${RESULT_TGZ}" | tee "${RESULT_SHA}"

echo "Goal1194 complete"
echo "result_tgz=${RESULT_TGZ}"
echo "result_sha=${RESULT_SHA}"
