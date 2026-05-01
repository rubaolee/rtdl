#!/usr/bin/env bash
set -euo pipefail

# Goal1176 pod-side executor for the reviewed Goal1175 staged source archive.
# Run on an already-running RTX-class Linux pod after uploading the archive.

ARCHIVE="${ARCHIVE:-/tmp/goal1175_rtdl_staged_source_2026-04-30.tar.gz}"
EXPECTED_SHA256="${EXPECTED_SHA256:-e6978ed37cdab26737df80efbcb1d34411900a66f9ce1c79063620d128bcce37}"
WORKDIR="${WORKDIR:-/workspace/rtdl_goal1176}"
SOURCE_DIR="${WORKDIR}/rtdl_staged_source"
RESULT_TGZ="${RESULT_TGZ:-/tmp/goal1176_goal1170_results.tgz}"
RESULT_SHA="${RESULT_SHA:-/tmp/goal1176_goal1170_results.tgz.sha256}"

echo "Goal1176 pod archive batch executor"
echo "archive=${ARCHIVE}"
echo "expected_sha256=${EXPECTED_SHA256}"
echo "workdir=${WORKDIR}"

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

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential git cmake pkg-config libgeos-dev python3-dev python3-pip \
  cuda-nvrtc-dev-13-0 cuda-cudart-dev-13-0

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
git commit -m "Goal1176 staged source archive"

export RTDL_SOURCE_COMMIT="goal1175-archive-${EXPECTED_SHA256}"

mkdir -p docs/reports/goal1170_clean_source_rtx_claim_grade_batch
{
  echo "Goal1176 environment"
  date -u
  uname -a
  nvidia-smi || true
  python3 --version || true
  sha256sum "${ARCHIVE}"
  echo "rtdl_source_commit=${RTDL_SOURCE_COMMIT}"
  git rev-parse HEAD
  git status --short
} | tee docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1176_environment.log

PYTHONPATH=src:. python3 scripts/goal1170_clean_source_rtx_batch_manifest.py \
  2>&1 | tee docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1170_manifest_generation.log

mkdir -p /root/vendor
if [ ! -d /root/vendor/optix-dev ]; then
  git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-dev.git /root/vendor/optix-dev
fi

export OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-dev}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export PYTHONPATH="${PYTHONPATH:-src:.}"

make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" CUDA_PREFIX="${CUDA_PREFIX}" NVCC="${NVCC}" \
  2>&1 | tee docs/reports/goal1170_clean_source_rtx_claim_grade_batch/make_build_optix.log

bash scripts/goal1170_clean_source_rtx_batch_runner.sh \
  2>&1 | tee docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1170_runner.log

tar -czf "${RESULT_TGZ}" docs/reports/goal1170_clean_source_rtx_claim_grade_batch
sha256sum "${RESULT_TGZ}" | tee "${RESULT_SHA}"

echo "Goal1176 complete"
echo "result_tgz=${RESULT_TGZ}"
echo "result_sha=${RESULT_SHA}"
