#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${APP_DIR}/../.." && pwd)"

WORK_DIR="${RAYJOIN_AUTHOR_WORK_DIR:-${APP_DIR}/_work/author_official}"
SRC_DIR="${RAYJOIN_AUTHOR_SRC_DIR:-${WORK_DIR}/RayJoin}"
BUILD_DIR="${RAYJOIN_AUTHOR_BUILD_DIR:-${WORK_DIR}/release}"
OPTIX_PREFIX="${OPTIX_PREFIX:-${HOME}/vendor/optix-dev}"
DEPS_DIR="${RAYJOIN_AUTHOR_DEPS_DIR:-${WORK_DIR}/deps}"
DEPS_INSTALL="${RAYJOIN_AUTHOR_DEPS_INSTALL:-${DEPS_DIR}/install}"

if [ -z "${RAYJOIN_CUDA_ARCH:-}" ]; then
  if command -v nvidia-smi >/dev/null 2>&1; then
    RAYJOIN_CUDA_ARCH="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n 1 | tr -d '.[:space:]' || true)"
  fi
fi
RAYJOIN_CUDA_ARCH="${RAYJOIN_CUDA_ARCH:-61}"

mkdir -p "${WORK_DIR}"

build_local_author_deps() {
  mkdir -p "${DEPS_DIR}" "${DEPS_INSTALL}"

  if [ ! -f "${DEPS_INSTALL}/include/gflags/gflags.h" ] || [ ! -e "${DEPS_INSTALL}/lib/libgflags.a" ]; then
    if [ ! -d "${DEPS_DIR}/gflags/.git" ]; then
      git clone --depth 1 --branch v2.2.2 https://github.com/gflags/gflags.git "${DEPS_DIR}/gflags"
    fi
    cmake -S "${DEPS_DIR}/gflags" -B "${DEPS_DIR}/gflags-build" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX="${DEPS_INSTALL}" \
      -DCMAKE_INSTALL_LIBDIR=lib \
      -DBUILD_SHARED_LIBS=OFF \
      -DGFLAGS_BUILD_TESTING=OFF \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON
    cmake --build "${DEPS_DIR}/gflags-build" -j"$(nproc)" --target install
  fi

  if [ ! -f "${DEPS_INSTALL}/include/glog/logging.h" ] || [ ! -e "${DEPS_INSTALL}/lib/libglog.a" ]; then
    if [ ! -d "${DEPS_DIR}/glog/.git" ]; then
      git clone --depth 1 --branch v0.6.0 https://github.com/google/glog.git "${DEPS_DIR}/glog"
    fi
    cmake -S "${DEPS_DIR}/glog" -B "${DEPS_DIR}/glog-build" \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX="${DEPS_INSTALL}" \
      -DCMAKE_INSTALL_LIBDIR=lib \
      -DCMAKE_PREFIX_PATH="${DEPS_INSTALL}" \
      -DBUILD_SHARED_LIBS=OFF \
      -DWITH_GFLAGS=ON \
      -DBUILD_TESTING=OFF \
      -DCMAKE_POSITION_INDEPENDENT_CODE=ON
    cmake --build "${DEPS_DIR}/glog-build" -j"$(nproc)" --target install
  fi
}

build_local_author_deps

if [ ! -d "${SRC_DIR}/.git" ]; then
  git clone https://github.com/pwrliang/RayJoin.git "${SRC_DIR}"
fi

cd "${SRC_DIR}"
git fetch --tags origin
git checkout 02bf622
git reset --hard 02bf622
git clean -fdx

git apply --whitespace=nowarn "${APP_DIR}/author_patches/author_clean_compat_cuda12.patch"
git apply --whitespace=nowarn "${APP_DIR}/author_patches/author_sos_t_reported.patch"
python3 "${APP_DIR}/scripts/apply_author_duplicate_contract_patch.py" "${SRC_DIR}"

python3 - "${RAYJOIN_CUDA_ARCH}" "${DEPS_INSTALL}/include" <<'PY'
import sys
from pathlib import Path
arch = sys.argv[1]
deps_include = sys.argv[2]
path = Path("src/CMakeLists.txt")
text = path.read_text()
text = text.replace('set(ENABLED_ARCHS "86")', f'set(ENABLED_ARCHS "{arch}")')
needle = '        "-I${CMAKE_CURRENT_SOURCE_DIR}"\n)'
replacement = f'        "-I${{CMAKE_CURRENT_SOURCE_DIR}}"\n        "-I{deps_include}"\n)'
if needle in text and deps_include not in text:
    text = text.replace(needle, replacement, 1)
path.write_text(text)
print(f"[author-setup] RayJoin CUDA architecture set to compute_{arch}")
print(f"[author-setup] RayJoin PTX include path added: {deps_include}")
PY

cmake -S "${SRC_DIR}" -B "${BUILD_DIR}" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH="${OPTIX_PREFIX};${DEPS_INSTALL}" \
  -DGFLAGS_ROOT_DIR="${DEPS_INSTALL}" \
  -DGLOG_ROOT_DIR="${DEPS_INSTALL}"
cmake --build "${BUILD_DIR}" -j"$(nproc)"

test -x "${BUILD_DIR}/bin/query_exec"
test -x "${BUILD_DIR}/bin/polyover_exec"

cat <<EOF
{
  "schema": "rtdl.paper_reproduction.rayjoin.author_official_setup.v1",
  "source": "${SRC_DIR}",
  "build": "${BUILD_DIR}",
  "commit": "$(git rev-parse HEAD)",
  "cuda_arch": "${RAYJOIN_CUDA_ARCH}",
  "query_exec": "${BUILD_DIR}/bin/query_exec",
  "polyover_exec": "${BUILD_DIR}/bin/polyover_exec"
}
EOF
