#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_URL="${AUTHOR_REPO:-https://github.com/vani-nag/OWLRayTracing.git}"
BRANCH="${AUTHOR_BRANCH:-rt-dbscan}"
COMMIT="${AUTHOR_COMMIT:-92749fe82ed001e5b7303265d4a2a73aa1bbf529}"
WORK_DIR="${WORK_DIR:-${APP_DIR}/_authorofficial_warm_work}"
SRC_DIR="${WORK_DIR}/OWLRayTracing"
BUILD_DIR="${WORK_DIR}/build"
BASE_PATCH="${APP_DIR}/author_patches/goal5092_authorofficial_core_count_output.patch"
WARM_PATCH="${APP_DIR}/author_patches/goal5104_authorofficial_warm_repeat_loop.patch"
OPTIX_ROOT_DIR="${OptiX_ROOT_DIR:-${OPTIX_ROOT_DIR:-${OPTIX_PREFIX:-}}}"
if [[ -z "${OPTIX_ROOT_DIR}" && -f /root/vendor/optix-dev/include/optix.h ]]; then
  OPTIX_ROOT_DIR="/root/vendor/optix-dev"
fi
C_COMPILER="${CC:-}"
CXX_COMPILER="${CXX:-}"
CUDA_HOST_COMPILER="${CMAKE_CUDA_HOST_COMPILER:-}"
if [[ -z "${C_COMPILER}" && -x /usr/bin/gcc-12 ]]; then
  C_COMPILER="/usr/bin/gcc-12"
fi
if [[ -z "${CXX_COMPILER}" && -x /usr/bin/g++-12 ]]; then
  CXX_COMPILER="/usr/bin/g++-12"
fi
if [[ -z "${CUDA_HOST_COMPILER}" && -n "${CXX_COMPILER}" ]]; then
  CUDA_HOST_COMPILER="${CXX_COMPILER}"
fi

require_command() {
  local name="$1"
  if ! command -v "${name}" >/dev/null 2>&1; then
    echo "missing required command: ${name}" >&2
    exit 2
  fi
}

require_command git
require_command cmake
if [[ -z "${OPTIX_ROOT_DIR}" || ! -f "${OPTIX_ROOT_DIR}/include/optix.h" ]]; then
  echo "missing OptiX SDK headers: set OptiX_ROOT_DIR, OPTIX_ROOT_DIR, or OPTIX_PREFIX" >&2
  exit 2
fi

mkdir -p "${WORK_DIR}"
if [[ ! -d "${SRC_DIR}/.git" ]]; then
  git clone --branch "${BRANCH}" "${REPO_URL}" "${SRC_DIR}"
fi

git -C "${SRC_DIR}" fetch origin "${BRANCH}"
git -C "${SRC_DIR}" checkout "${COMMIT}"
git -C "${SRC_DIR}" reset --hard "${COMMIT}"
git -C "${SRC_DIR}" apply "${BASE_PATCH}"
git -C "${SRC_DIR}" apply "${WARM_PATCH}"

cmake_args=(
  -S "${SRC_DIR}"
  -B "${BUILD_DIR}"
  -DOptiX_ROOT_DIR="${OPTIX_ROOT_DIR}"
)
if [[ -n "${C_COMPILER}" ]]; then
  cmake_args+=(-DCMAKE_C_COMPILER="${C_COMPILER}")
fi
if [[ -n "${CXX_COMPILER}" ]]; then
  cmake_args+=(-DCMAKE_CXX_COMPILER="${CXX_COMPILER}")
fi
if [[ -n "${CUDA_HOST_COMPILER}" ]]; then
  cmake_args+=(-DCMAKE_CUDA_HOST_COMPILER="${CUDA_HOST_COMPILER}")
fi

cmake "${cmake_args[@]}"
cmake --build "${BUILD_DIR}" --target sample02-rtdbscan -j"$(nproc)"

BIN="$(find "${BUILD_DIR}" -type f -name sample02-rtdbscan -perm -111 | head -n 1)"
if [[ -z "${BIN}" ]]; then
  echo "sample02-rtdbscan binary not found under ${BUILD_DIR}" >&2
  exit 2
fi

echo "${BIN}"
