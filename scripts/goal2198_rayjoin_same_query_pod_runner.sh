#!/usr/bin/env bash
set -euo pipefail

GOAL="goal2198"
WORK_DIR="${WORK_DIR:-/root/goal2198_rayjoin_same_query_pod}"
OUT_DIR="${OUT_DIR:-${WORK_DIR}/artifacts}"
RTDL_REPO="${RTDL_REPO:-https://github.com/rubaolee/rtdl.git}"
RTDL_REF="${RTDL_REF:-main}"
RAYJOIN_REPO="${RAYJOIN_REPO:-https://github.com/rubaolee/RayJoin.git}"
RAYJOIN_COMMIT="${RAYJOIN_COMMIT:-02bf6220d6d20b04af77ee20364eced75cc029c9}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
OPTIX_TAG="${OPTIX_TAG:-v8.0.0}"
CUDA_PREFIX="${CUDA_PREFIX:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
USE_PYTHON_VENV="${USE_PYTHON_VENV:-1}"
VENV_DIR="${VENV_DIR:-${WORK_DIR}/.venv}"
GEN_N="${GEN_N:-100000}"
GEN_T="${GEN_T:-0.1}"
SEED="${SEED:-2184}"
WARMUP="${WARMUP:-1}"
REPEAT="${REPEAT:-3}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-1800}"
RUN_APT_INSTALL="${RUN_APT_INSTALL:-1}"
RUN_PIP_INSTALL="${RUN_PIP_INSTALL:-1}"
ALLOW_NON_CUDA12="${ALLOW_NON_CUDA12:-0}"

RTDL_DIR="${WORK_DIR}/rtdl"
RAYJOIN_DIR="${WORK_DIR}/RayJoin"
PROGRESS_LOG="${OUT_DIR}/progress.log"

mkdir -p "${OUT_DIR}"

log() {
  echo "[${GOAL}] $(date -Iseconds) $*" | tee -a "${PROGRESS_LOG}"
}

run_step() {
  local name="$1"
  shift
  log "start ${name}"
  if [[ "${STEP_TIMEOUT_SECONDS}" == "0" ]]; then
    "$@" 2>&1 | tee "${OUT_DIR}/${name}.log"
    local status=${PIPESTATUS[0]}
  else
    timeout --preserve-status "${STEP_TIMEOUT_SECONDS}s" "$@" 2>&1 | tee "${OUT_DIR}/${name}.log"
    local status=${PIPESTATUS[0]}
  fi
  if [[ "${status}" != "0" ]]; then
    log "fail ${name} status=${status}; see ${OUT_DIR}/${name}.log"
    exit "${status}"
  fi
  log "done ${name}"
}

detect_cuda_prefix() {
  if [[ -n "${CUDA_PREFIX}" && -x "${CUDA_PREFIX}/bin/nvcc" ]]; then
    echo "${CUDA_PREFIX}"
    return
  fi
  for candidate in /usr/local/cuda-12.8 /usr/local/cuda-12 /usr/local/cuda; do
    if [[ -x "${candidate}/bin/nvcc" ]]; then
      echo "${candidate}"
      return
    fi
  done
  if command -v nvcc >/dev/null 2>&1; then
    dirname "$(dirname "$(command -v nvcc)")"
    return
  fi
  echo ""
}

detect_cuda_major() {
  local version_text
  version_text="$("${CUDA_PREFIX}/bin/nvcc" --version 2>/dev/null || true)"
  echo "${version_text}" | sed -n 's/.*release \([0-9][0-9]*\)\..*/\1/p' | head -n 1
}

detect_cuda_major_minor_dash() {
  local version_text
  version_text="$("${CUDA_PREFIX}/bin/nvcc" --version 2>/dev/null || true)"
  echo "${version_text}" | sed -n 's/.*release \([0-9][0-9]*\)\.\([0-9][0-9]*\).*/\1-\2/p' | head -n 1
}

require_cuda12_for_cupy_package() {
  local cuda_major
  cuda_major="$(detect_cuda_major)"
  if [[ "${cuda_major}" == "12" ]]; then
    log "CUDA major ${cuda_major} matches cupy-cuda12x"
    return
  fi
  if [[ "${ALLOW_NON_CUDA12}" == "1" ]]; then
    log "warning: CUDA major ${cuda_major:-unknown} does not match cupy-cuda12x; continuing because ALLOW_NON_CUDA12=1"
    return
  fi
  log "CUDA major ${cuda_major:-unknown} does not match cupy-cuda12x; set CUDA_PREFIX to CUDA 12.x or ALLOW_NON_CUDA12=1 for manual debugging"
  exit 5
}

install_cuda_nvtx_if_available() {
  local cuda_major_minor
  cuda_major_minor="$(detect_cuda_major_minor_dash)"
  if [[ -z "${cuda_major_minor}" ]]; then
    log "could not infer CUDA major/minor for optional NVTX package"
    return
  fi
  local package="cuda-nvtx-${cuda_major_minor}"
  if dpkg -s "${package}" >/dev/null 2>&1; then
    log "${package} already installed"
    return
  fi
  if apt-cache show "${package}" >/dev/null 2>&1; then
    run_step "apt_install_${package}" env DEBIAN_FRONTEND=noninteractive apt-get install -y "${package}"
    return
  fi
  log "${package} not available; relying on CUDA include tree for NVTX headers"
}

install_host_dependencies() {
  if [[ "${RUN_APT_INSTALL}" != "1" ]]; then
    log "skip apt dependency install because RUN_APT_INSTALL=${RUN_APT_INSTALL}"
    return
  fi
  if ! command -v apt-get >/dev/null 2>&1; then
    log "apt-get missing; skipping apt dependency install"
    return
  fi
  run_step apt_update apt-get update
  run_step apt_install env DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    ca-certificates \
    cmake \
    git \
    libboost-filesystem-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libembree-dev \
    libgeos-dev \
    libgflags-dev \
    libgoogle-glog-dev \
    libtbb-dev \
    ninja-build \
    nlohmann-json3-dev \
    python3 \
    python3-pip \
    python3-venv
  install_cuda_nvtx_if_available
}

prepare_python_environment() {
  if [[ "${RUN_PIP_INSTALL}" != "1" ]]; then
    log "skip Python venv preparation because RUN_PIP_INSTALL=${RUN_PIP_INSTALL}"
    return
  fi
  if [[ "${USE_PYTHON_VENV}" != "1" ]]; then
    log "using caller-provided Python environment: ${PYTHON_BIN}"
    return
  fi
  local bootstrap_python="${PYTHON_BIN}"
  run_step create_python_venv "${bootstrap_python}" -m venv "${VENV_DIR}"
  PYTHON_BIN="${VENV_DIR}/bin/python"
  log "using Python venv ${VENV_DIR}"
}

install_optix_sdk_if_needed() {
  if [[ -f "${OPTIX_PREFIX}/include/optix.h" ]]; then
    log "OptiX SDK present at ${OPTIX_PREFIX}"
  else
    log "installing OptiX SDK headers ${OPTIX_TAG} into ${OPTIX_PREFIX}"
    mkdir -p "$(dirname "${OPTIX_PREFIX}")"
    rm -rf "${OPTIX_PREFIX}"
    run_step clone_optix_sdk git clone --depth 1 --branch "${OPTIX_TAG}" https://github.com/NVIDIA/optix-sdk "${OPTIX_PREFIX}"
  fi
  ln -sfn "${OPTIX_PREFIX}" /opt/optix || true
}

clone_or_update_rtdl() {
  mkdir -p "${WORK_DIR}"
  if [[ ! -d "${RTDL_DIR}/.git" ]]; then
    run_step clone_rtdl git clone "${RTDL_REPO}" "${RTDL_DIR}"
  fi
  run_step fetch_rtdl git -C "${RTDL_DIR}" fetch --all --tags
  run_step checkout_rtdl git -C "${RTDL_DIR}" checkout "${RTDL_REF}"
  if git -C "${RTDL_DIR}" show-ref --verify --quiet "refs/remotes/origin/${RTDL_REF}"; then
    run_step reset_rtdl git -C "${RTDL_DIR}" reset --hard "origin/${RTDL_REF}"
  fi
}

clone_or_update_rayjoin() {
  mkdir -p "${WORK_DIR}"
  if [[ ! -d "${RAYJOIN_DIR}/.git" ]]; then
    run_step clone_rayjoin git clone "${RAYJOIN_REPO}" "${RAYJOIN_DIR}"
  fi
  run_step fetch_rayjoin git -C "${RAYJOIN_DIR}" fetch --all --tags
  run_step checkout_rayjoin git -C "${RAYJOIN_DIR}" checkout "${RAYJOIN_COMMIT}"
  run_step clean_rayjoin git -C "${RAYJOIN_DIR}" clean -fdx
  run_step reset_rayjoin git -C "${RAYJOIN_DIR}" reset --hard "${RAYJOIN_COMMIT}"
}

apply_rayjoin_build_compatibility_fixes() {
  run_step patch_rayjoin_build_compat "${PYTHON_BIN}" - "${RAYJOIN_DIR}" <<'PY'
from __future__ import annotations

import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])

cmake = root / "src" / "CMakeLists.txt"
text = cmake.read_text(encoding="utf-8")
text = re.sub(r"set\(\s*ENABLED_ARCHS\s+\"?[0-9; ]+\"?\s*\)", "set(ENABLED_ARCHS 86)", text)
cmake.write_text(text, encoding="utf-8")

markers = root / "src" / "util" / "markers.h"
text = markers.read_text(encoding="utf-8")
text = text.replace("#include <nvToolsExt.h>", "#include <nvtx3/nvToolsExt.h>")
markers.write_text(text, encoding="utf-8")

output_chain = root / "src" / "app" / "output_chain.h"
text = output_chain.read_text(encoding="utf-8")
helper = r"""
#ifndef RTDL_GOAL2198_VEC2_HASH_EQUAL_PATCH
#define RTDL_GOAL2198_VEC2_HASH_EQUAL_PATCH
template <typename PointT>
struct Goal2198Vec2Hash {
  size_t operator()(const PointT& p) const {
    return std::hash<decltype(p.x)>{}(p.x) ^
           (std::hash<decltype(p.y)>{}(p.y) << 1);
  }
};
template <typename PointT>
struct Goal2198Vec2Equal {
  bool operator()(const PointT& a, const PointT& b) const {
    return a.x == b.x && a.y == b.y;
  }
};
#endif
"""
if "RTDL_GOAL2198_VEC2_HASH_EQUAL_PATCH" not in text:
    insert_at = text.find("namespace")
    if insert_at < 0:
        raise SystemExit("output_chain.h: could not locate namespace insertion point")
    text = text[:insert_at] + helper + "\n" + text[insert_at:]

old = "std::unordered_map<typename cuda_vec<coord_t>::type_2d, index_t> point_ids;"
new = (
    "std::unordered_map<"
    "typename cuda_vec<coord_t>::type_2d, "
    "index_t, "
    "Goal2198Vec2Hash<typename cuda_vec<coord_t>::type_2d>, "
    "Goal2198Vec2Equal<typename cuda_vec<coord_t>::type_2d>> point_ids;"
)
if old in text:
    text = text.replace(old, new)
elif "Goal2198Vec2Hash<typename cuda_vec<coord_t>::type_2d>" not in text:
    raise SystemExit("output_chain.h: unordered_map target not found and not already patched")
output_chain.write_text(text, encoding="utf-8")
PY
}

apply_goal2195_export_patch() {
  local patch_path="${RTDL_DIR}/docs/reports/goal2195_rayjoin_query_exec_export_patch_2026-05-17.diff"
  if [[ ! -f "${patch_path}" ]]; then
    log "missing expected export patch: ${patch_path}"
    exit 3
  fi
  run_step check_goal2195_patch git -C "${RAYJOIN_DIR}" apply --check "${patch_path}"
  run_step apply_goal2195_patch git -C "${RAYJOIN_DIR}" apply "${patch_path}"
}

install_python_dependencies() {
  if [[ "${RUN_PIP_INSTALL}" != "1" ]]; then
    log "skip Python dependency install because RUN_PIP_INSTALL=${RUN_PIP_INSTALL}"
    return
  fi
  run_step pip_install_core "${PYTHON_BIN}" -m pip install --upgrade pip setuptools wheel
  run_step pip_install_runtime "${PYTHON_BIN}" -m pip install numpy cupy-cuda12x
}

build_rayjoin() {
  run_step configure_rayjoin cmake \
    -S "${RAYJOIN_DIR}" \
    -B "${RAYJOIN_DIR}/release" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH="${OPTIX_PREFIX}" \
    -DCMAKE_CUDA_COMPILER="${CUDA_PREFIX}/bin/nvcc"
  run_step build_rayjoin cmake --build "${RAYJOIN_DIR}/release" -j"$(nproc)"
}

build_rtdl() {
  run_step build_rtdl_embree make -C "${RTDL_DIR}" build-embree
  run_step build_rtdl_optix make -C "${RTDL_DIR}" build-optix OPTIX_PREFIX="${OPTIX_PREFIX}" CUDA_PREFIX="${CUDA_PREFIX}"
}

run_rayjoin_query() {
  local workload="$1"
  local mode="$2"
  local stream_output="${3:-}"
  local dataset="${RAYJOIN_DATASET:-${RAYJOIN_DIR}/test/dataset/br_county_clean_25_odyssey_final.txt}"
  local args=(
    "${RAYJOIN_DIR}/release/bin/query_exec"
    "-poly1=${dataset}"
    "-query=${workload}"
    "-mode=${mode}"
    "-gen_n=${GEN_N}"
    "-gen_t=${GEN_T}"
    "-seed=${SEED}"
    "-warmup=${WARMUP}"
    "-repeat=${REPEAT}"
  )
  if [[ "${workload}" == "pip" && "${mode}" == "rt" ]]; then
    args+=("-check=true")
  fi
  if [[ -n "${stream_output}" ]]; then
    args+=("-query_stream_output=${stream_output}")
  fi
  run_step "rayjoin_${workload}_${mode}" "${args[@]}"
}

run_rtdl_same_stream() {
  local workload="$1"
  local stream_path="${OUT_DIR}/rayjoin_${workload}_gen${GEN_N}_stream.json"
  local result_path="${OUT_DIR}/rtdl_${workload}_same_rayjoin_stream.json"
  run_step "rtdl_${workload}_same_stream" env \
    PYTHONPATH="${RTDL_DIR}/src:${RTDL_DIR}" \
    RTDL_EMBREE_LIBRARY="${RTDL_DIR}/build/librtdl_embree.so" \
    RTDL_OPTIX_LIBRARY="${RTDL_DIR}/build/librtdl_optix.so" \
    CUDA_HOME="${CUDA_PREFIX}" \
    PATH="${CUDA_PREFIX}/bin:${PATH}" \
    LD_LIBRARY_PATH="${CUDA_PREFIX}/targets/x86_64-linux/lib:${CUDA_PREFIX}/lib64:${CUDA_PREFIX}/compat:${LD_LIBRARY_PATH:-}" \
    RTDL_OPTIX_PTX_ARCH="${RTDL_OPTIX_PTX_ARCH:-compute_86}" \
    RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}" \
    RTDL_NVCC="${CUDA_PREFIX}/bin/nvcc" \
    "${PYTHON_BIN}" "${RTDL_DIR}/scripts/goal2192_rayjoin_same_query_stream_runner.py" run-stream \
      --query-stream "${stream_path}" \
      --output "${result_path}" \
      --backends cpu,embree,optix \
      --reference-backend cpu \
      --warmups "${WARMUP}" \
      --repeats "${REPEAT}"
}

write_environment() {
  {
    echo "goal=${GOAL}"
    echo "work_dir=${WORK_DIR}"
    echo "out_dir=${OUT_DIR}"
    echo "rtdl_repo=${RTDL_REPO}"
    echo "rtdl_ref=${RTDL_REF}"
    echo "rayjoin_repo=${RAYJOIN_REPO}"
    echo "rayjoin_commit=${RAYJOIN_COMMIT}"
    echo "optix_prefix=${OPTIX_PREFIX}"
    echo "optix_tag=${OPTIX_TAG}"
    echo "cuda_prefix=${CUDA_PREFIX}"
    echo "python=$(${PYTHON_BIN} --version 2>&1)"
    echo "use_python_venv=${USE_PYTHON_VENV}"
    echo "venv_dir=${VENV_DIR}"
    echo "gen_n=${GEN_N}"
    echo "gen_t=${GEN_T}"
    echo "seed=${SEED}"
    echo "warmup=${WARMUP}"
    echo "repeat=${REPEAT}"
    uname -a || true
    if [[ -f /etc/os-release ]]; then cat /etc/os-release; fi
    if command -v nvidia-smi >/dev/null 2>&1; then
      nvidia-smi
      nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true
    fi
    ls -d /usr/local/cuda* 2>/dev/null || true
    command -v nvcc || true
    "${CUDA_PREFIX}/bin/nvcc" --version || true
    find /usr /lib /run -name 'libnvoptix*' 2>/dev/null | head -20 || true
  } | tee "${OUT_DIR}/environment.txt"
}

write_summary() {
  run_step write_summary "${PYTHON_BIN}" - "${OUT_DIR}" "${RTDL_DIR}" "${RAYJOIN_DIR}" "${RAYJOIN_COMMIT}" <<'PY'
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

out_dir = pathlib.Path(sys.argv[1])
rtdl_dir = pathlib.Path(sys.argv[2])
rayjoin_dir = pathlib.Path(sys.argv[3])
rayjoin_commit = sys.argv[4]

def git_commit(path: pathlib.Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()

results = {}
for workload in ("lsi", "pip"):
    artifact = out_dir / f"rtdl_{workload}_same_rayjoin_stream.json"
    data = json.loads(artifact.read_text(encoding="utf-8"))
    if data["query_stream_producer"] != "rayjoin_query_exec_export_patch":
        raise SystemExit(f"{artifact}: expected RayJoin-exported stream")
    boundary = data["claim_boundary"]
    if not boundary.get("same_contract_with_rayjoin_query_exec"):
        raise SystemExit(f"{artifact}: expected same-contract flag")
    for blocked_key in (
        "paper_scale_perf_claim_authorized",
        "rtdl_beats_rayjoin_claim_authorized",
        "v2_0_release_authorized",
    ):
        if boundary.get(blocked_key):
            raise SystemExit(f"{artifact}: {blocked_key} unexpectedly true")
    for backend_name, backend in data["backends"].items():
        if not backend.get("all_parity_vs_cpu_python_reference"):
            raise SystemExit(f"{artifact}: {backend_name} parity failed")
    results[workload] = {
        "query_count": data["query_count"],
        "stream": str(out_dir / f"rayjoin_{workload}_gen{data['query_count']}_stream.json"),
        "rtdl_artifact": str(artifact),
        "backends": data["backends"],
    }

summary = {
    "goal": "2198",
    "status": "pass",
    "rtdl_commit": git_commit(rtdl_dir),
    "rayjoin_commit": git_commit(rayjoin_dir),
    "expected_rayjoin_commit": rayjoin_commit,
    "schema": "rtdl.rayjoin.same_query_stream.v1",
    "results": results,
    "rayjoin_logs": {
        "lsi_grid": str(out_dir / "rayjoin_lsi_grid.log"),
        "lsi_lbvh": str(out_dir / "rayjoin_lsi_lbvh.log"),
        "lsi_rt": str(out_dir / "rayjoin_lsi_rt.log"),
        "pip_grid": str(out_dir / "rayjoin_pip_grid.log"),
        "pip_lbvh": str(out_dir / "rayjoin_pip_lbvh.log"),
        "pip_rt": str(out_dir / "rayjoin_pip_rt.log"),
    },
    "claim_boundary": {
        "same_contract_with_rayjoin_query_exec": True,
        "paper_scale_perf_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "broad_rt_core_speedup_claim_authorized": False,
        "v2_0_release_authorized": False,
    },
}
(out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2, sort_keys=True))
PY
  run_step write_evidence_report env PYTHONPATH="${RTDL_DIR}/src:${RTDL_DIR}" "${PYTHON_BIN}" \
    "${RTDL_DIR}/scripts/goal2201_rayjoin_same_query_evidence_report.py" \
    --artifact-dir "${OUT_DIR}" \
    --output-json "${OUT_DIR}/evidence_summary.json" \
    --output-md "${OUT_DIR}/evidence_report.md"
}

main() {
  log "begin RayJoin same-query RTX pod run"
  CUDA_PREFIX="$(detect_cuda_prefix)"
  if [[ -z "${CUDA_PREFIX}" || ! -x "${CUDA_PREFIX}/bin/nvcc" ]]; then
    log "CUDA nvcc not found; set CUDA_PREFIX"
    exit 4
  fi
  require_cuda12_for_cupy_package
  export CUDA_HOME="${CUDA_PREFIX}"
  export PATH="${CUDA_PREFIX}/bin:${PATH}"
  export LD_LIBRARY_PATH="${CUDA_PREFIX}/targets/x86_64-linux/lib:${CUDA_PREFIX}/lib64:${CUDA_PREFIX}/compat:${LD_LIBRARY_PATH:-}"
  export RTDL_OPTIX_PTX_ARCH="${RTDL_OPTIX_PTX_ARCH:-compute_86}"
  export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
  export RTDL_NVCC="${CUDA_PREFIX}/bin/nvcc"

  write_environment
  install_host_dependencies
  prepare_python_environment
  install_python_dependencies
  install_optix_sdk_if_needed
  clone_or_update_rtdl
  clone_or_update_rayjoin
  apply_rayjoin_build_compatibility_fixes
  apply_goal2195_export_patch
  build_rayjoin
  build_rtdl

  run_rayjoin_query lsi grid
  run_rayjoin_query lsi lbvh
  run_rayjoin_query lsi rt "${OUT_DIR}/rayjoin_lsi_gen${GEN_N}_stream.json"
  run_rayjoin_query pip grid
  run_rayjoin_query pip lbvh
  run_rayjoin_query pip rt "${OUT_DIR}/rayjoin_pip_gen${GEN_N}_stream.json"

  run_rtdl_same_stream lsi
  run_rtdl_same_stream pip
  write_summary
  log "complete; summary=${OUT_DIR}/summary.json"
}

main "$@"
