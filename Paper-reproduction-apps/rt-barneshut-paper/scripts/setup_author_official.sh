#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
WORK_DIR="${APP_DIR}/_work/author_official"
SRC_DIR="${WORK_DIR}/OWLRayTracing"
BUILD_DIR="${SRC_DIR}/build-rtdl-rtbarneshut"

AUTHOR_REPO="${AUTHOR_REPO:-https://github.com/vani-nag/OWLRayTracing}"
AUTHOR_BRANCH="${AUTHOR_BRANCH:-BarnesHutRT}"
AUTHOR_COMMIT="${AUTHOR_COMMIT:-2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7}"
CUDA_ARCH="${CUDA_ARCH:-86}"
RTBH_NUM_POINTS="${RTBH_NUM_POINTS:-32768}"

detect_optix_root_dir() {
  if [ -n "${OPTIX_ROOT_DIR:-}" ]; then
    printf '%s\n' "${OPTIX_ROOT_DIR}"
    return
  fi
  if [ -n "${OPTIX_PREFIX:-}" ]; then
    printf '%s\n' "${OPTIX_PREFIX}"
    return
  fi
  if [ -n "${OptiX_INSTALL_DIR:-}" ]; then
    printf '%s\n' "${OptiX_INSTALL_DIR}"
    return
  fi
  for candidate in \
    /root/vendor/optix-dev \
    /root/vendor/optix-sdk \
    /workspace/vendor/optix-dev \
    /workspace/vendor/optix-sdk \
    /workspace/vendor/optix-dev-9.0.0 \
    /workspace/vendor/optix-dev-8.1.0 \
    /workspace/vendor/optix-dev-8.0.0 \
    /opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64 \
    /opt/optix; do
    if [ -f "${candidate}/include/optix.h" ]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done
  printf '%s\n' "/opt/optix/NVIDIA-OptiX-SDK-8.1.0-linux64-x86_64"
}

detect_cuda_prefix() {
  if [ -n "${CUDA_PREFIX:-}" ]; then
    printf '%s\n' "${CUDA_PREFIX}"
    return
  fi
  if [ -n "${CUDA_HOME:-}" ] && [ -x "${CUDA_HOME}/bin/nvcc" ]; then
    printf '%s\n' "${CUDA_HOME}"
    return
  fi
  for candidate in /usr/local/cuda /usr/local/cuda-13.0 /usr/local/cuda-12.8 /usr/local/cuda-12.6 /usr/local/cuda-12.5; do
    if [ -x "${candidate}/bin/nvcc" ]; then
      printf '%s\n' "${candidate}"
      return
    fi
  done
  printf '%s\n' "/usr/local/cuda"
}

OPTIX_ROOT_DIR="$(detect_optix_root_dir)"
CUDA_PREFIX="$(detect_cuda_prefix)"

CMAKE_TBB_ARGS=()
if [ -f /usr/include/tbb/version.h ] && [ -f /usr/lib/x86_64-linux-gnu/libtbb.so ] && [ -f /usr/lib/x86_64-linux-gnu/libtbbmalloc.so ]; then
  # The pinned OWL FindTBB module predates oneTBB on modern Ubuntu and looks
  # for removed headers/libraries.  Supplying the resolved compatibility paths
  # avoids a false configure failure without changing author algorithm logic.
  CMAKE_TBB_ARGS+=(
    -DTBB_INCLUDE_DIR=/usr/include
    -DTBB_LIBRARY=/usr/lib/x86_64-linux-gnu/libtbb.so
    -DTBB_LIBRARY_MALLOC=/usr/lib/x86_64-linux-gnu/libtbbmalloc.so
  )
fi

mkdir -p "${WORK_DIR}"

if [ ! -d "${SRC_DIR}/.git" ]; then
  git clone --branch "${AUTHOR_BRANCH}" "${AUTHOR_REPO}" "${SRC_DIR}"
fi

cd "${SRC_DIR}"
git fetch origin "${AUTHOR_BRANCH}"
git -c advice.detachedHead=false checkout --force "${AUTHOR_COMMIT}"
git reset --hard "${AUTHOR_COMMIT}"

AUTHOR_SAMPLE_DIR="${SRC_DIR}/samples/cmdline/s01-rtbarneshut"
if [ ! -d "${AUTHOR_SAMPLE_DIR}" ]; then
  echo "Could not find author sample directory: ${AUTHOR_SAMPLE_DIR}" >&2
  exit 2
fi

python3 "${APP_DIR}/scripts/apply_author_official_patch.py" \
  --source-root "${SRC_DIR}" \
  --body-count "${RTBH_NUM_POINTS}"

cmake -S . -B "${BUILD_DIR}" \
  -DCMAKE_BUILD_TYPE=Release \
  -DOptiX_ROOT_DIR="${OPTIX_ROOT_DIR}" \
  -DCMAKE_CUDA_COMPILER="${CUDA_PREFIX}/bin/nvcc" \
  -DCUDAToolkit_ROOT="${CUDA_PREFIX}" \
  -DCMAKE_CUDA_ARCHITECTURES="${CUDA_ARCH}" \
  -DCMAKE_CUDA_FLAGS="-include array" \
  -DBUILD_TESTING=OFF \
  "${CMAKE_TBB_ARGS[@]}"

cmake --build "${BUILD_DIR}" --target rtbarneshut -j"$(nproc)"

echo "AuthorOfficial build complete: ${BUILD_DIR}/rtbarneshut"
