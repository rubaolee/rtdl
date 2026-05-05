#!/usr/bin/env bash
set -euo pipefail

OUTPUT_ENV="${OUTPUT_ENV:-/tmp/rtdl_pod_env.sh}"
OUTPUT_JSON="${OUTPUT_JSON:-/tmp/rtdl_pod_env.json}"
INSTALL_DEPS="${INSTALL_DEPS:-1}"
OPTIX_GIT_REF="${OPTIX_GIT_REF:-v8.0.0}"
OPTIX_VENDOR_DIR="${OPTIX_VENDOR_DIR:-/root/vendor/optix-dev}"

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'
}

detect_os_id() {
  if [ -r /etc/os-release ]; then
    . /etc/os-release
    printf '%s' "${ID:-unknown}"
  else
    uname -s | tr '[:upper:]' '[:lower:]'
  fi
}

install_base_packages() {
  if [ "${INSTALL_DEPS}" != "1" ]; then
    return
  fi
  if command_exists apt-get; then
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y build-essential git cmake pkg-config libgeos-dev libembree-dev python3-dev python3-pip
    if ! command_exists nvcc; then
      apt-get install -y cuda-nvcc-13-0 cuda-nvrtc-dev-13-0 cuda-cudart-dev-13-0 || \
      apt-get install -y cuda-nvcc-12-8 cuda-nvrtc-dev-12-8 cuda-cudart-dev-12-8 || \
      apt-get install -y nvidia-cuda-toolkit || true
    fi
  elif command_exists dnf; then
    dnf install -y gcc gcc-c++ make git cmake pkgconf-pkg-config geos-devel embree-devel python3-devel python3-pip || true
  elif command_exists yum; then
    yum install -y gcc gcc-c++ make git cmake pkgconfig geos-devel embree-devel python3-devel python3-pip || true
  elif command_exists apk; then
    apk add --no-cache build-base git cmake pkgconf geos-dev python3-dev py3-pip || true
  fi
}

detect_cuda_prefix() {
  if [ -n "${CUDA_PREFIX:-}" ] && [ -d "${CUDA_PREFIX}" ]; then
    printf '%s' "${CUDA_PREFIX}"
    return
  fi
  if [ -n "${NVCC:-}" ] && [ -x "${NVCC}" ]; then
    dirname "$(dirname "${NVCC}")"
    return
  fi
  if command_exists nvcc; then
    dirname "$(dirname "$(command -v nvcc)")"
    return
  fi
  for candidate in /usr/local/cuda /usr/local/cuda-* /usr/lib/cuda /opt/cuda; do
    if [ -x "${candidate}/bin/nvcc" ] || [ -d "${candidate}/include" ]; then
      printf '%s' "${candidate}"
      return
    fi
  done
  printf '%s' "/usr/local/cuda"
}

detect_nvcc() {
  local cuda_prefix="$1"
  if [ -n "${NVCC:-}" ] && [ -x "${NVCC}" ]; then
    printf '%s' "${NVCC}"
    return
  fi
  if [ -x "${cuda_prefix}/bin/nvcc" ]; then
    printf '%s' "${cuda_prefix}/bin/nvcc"
    return
  fi
  if command_exists nvcc; then
    command -v nvcc
    return
  fi
  for candidate in /usr/local/cuda*/bin/nvcc /usr/lib/cuda/bin/nvcc /opt/cuda/bin/nvcc; do
    if [ -x "${candidate}" ]; then
      printf '%s' "${candidate}"
      return
    fi
  done
  printf '%s' "${cuda_prefix}/bin/nvcc"
}

detect_optix_prefix() {
  if [ -n "${OPTIX_PREFIX:-}" ] && [ -f "${OPTIX_PREFIX}/include/optix.h" ]; then
    printf '%s' "${OPTIX_PREFIX}"
    return
  fi
  for candidate in \
    /root/vendor/optix-dev \
    /workspace/vendor/optix-dev \
    /workspace/vendor/optix-dev-8.0.0 \
    /workspace/vendor/optix-dev-9.0.0 \
    "${HOME:-/root}/vendor/optix-dev" \
    "${HOME:-/root}/vendor/optix" \
    /opt/optix \
    /usr/local/optix \
    /usr/local/NVIDIA-OptiX-SDK*; do
    if [ -f "${candidate}/include/optix.h" ]; then
      printf '%s' "${candidate}"
      return
    fi
  done
  if command_exists git; then
    mkdir -p "$(dirname "${OPTIX_VENDOR_DIR}")"
    if [ ! -d "${OPTIX_VENDOR_DIR}/.git" ]; then
      git clone --depth 1 --branch "${OPTIX_GIT_REF}" https://github.com/NVIDIA/optix-dev.git "${OPTIX_VENDOR_DIR}" || \
      git clone --depth 1 https://github.com/NVIDIA/optix-dev.git "${OPTIX_VENDOR_DIR}"
    fi
    if [ -f "${OPTIX_VENDOR_DIR}/include/optix.h" ]; then
      printf '%s' "${OPTIX_VENDOR_DIR}"
      return
    fi
  fi
  printf '%s' "${OPTIX_PREFIX:-/opt/optix}"
}

install_base_packages

OS_ID="$(detect_os_id)"
CUDA_PREFIX_DETECTED="$(detect_cuda_prefix)"
NVCC_DETECTED="$(detect_nvcc "${CUDA_PREFIX_DETECTED}")"
OPTIX_PREFIX_DETECTED="$(detect_optix_prefix)"
CUDA_LIB_DIR="${CUDA_PREFIX_DETECTED}/lib64"
if [ ! -d "${CUDA_LIB_DIR}" ]; then
  CUDA_LIB_DIR="/usr/lib/x86_64-linux-gnu"
fi

mkdir -p "$(dirname "${OUTPUT_ENV}")" "$(dirname "${OUTPUT_JSON}")"
cat > "${OUTPUT_ENV}" <<EOF
export RTDL_POD_OS_ID="${OS_ID}"
export CUDA_PREFIX="${CUDA_PREFIX_DETECTED}"
export NVCC="${NVCC_DETECTED}"
export RTDL_NVCC="${NVCC_DETECTED}"
export OPTIX_PREFIX="${OPTIX_PREFIX_DETECTED}"
export RTDL_OPTIX_PTX_COMPILER="\${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export LD_LIBRARY_PATH="${CUDA_LIB_DIR}:/usr/lib/x86_64-linux-gnu:\${LD_LIBRARY_PATH:-}"
EOF

NVCC_VERSION=""
if [ -x "${NVCC_DETECTED}" ]; then
  NVCC_VERSION="$("${NVCC_DETECTED}" --version 2>&1 | tail -n 5 || true)"
fi
NVIDIA_SMI=""
if command_exists nvidia-smi; then
  NVIDIA_SMI="$(nvidia-smi 2>&1 | head -n 40 || true)"
fi

cat > "${OUTPUT_JSON}" <<EOF
{
  "goal": "RTDL pod environment probe",
  "os_id": $(printf '%s' "${OS_ID}" | json_escape),
  "package_manager": $(if command_exists apt-get; then printf apt-get; elif command_exists dnf; then printf dnf; elif command_exists yum; then printf yum; elif command_exists apk; then printf apk; else printf none; fi | json_escape),
  "cuda_prefix": $(printf '%s' "${CUDA_PREFIX_DETECTED}" | json_escape),
  "nvcc": $(printf '%s' "${NVCC_DETECTED}" | json_escape),
  "nvcc_exists": $(if [ -x "${NVCC_DETECTED}" ]; then printf true; else printf false; fi),
  "optix_prefix": $(printf '%s' "${OPTIX_PREFIX_DETECTED}" | json_escape),
  "optix_header_exists": $(if [ -f "${OPTIX_PREFIX_DETECTED}/include/optix.h" ]; then printf true; else printf false; fi),
  "cuda_lib_dir": $(printf '%s' "${CUDA_LIB_DIR}" | json_escape),
  "nvcc_version_tail": $(printf '%s' "${NVCC_VERSION}" | json_escape),
  "nvidia_smi_tail": $(printf '%s' "${NVIDIA_SMI}" | json_escape),
  "env_file": $(printf '%s' "${OUTPUT_ENV}" | json_escape),
  "boundary": "Environment probe only; no benchmark or public speedup claim is authorized."
}
EOF

cat "${OUTPUT_ENV}"
