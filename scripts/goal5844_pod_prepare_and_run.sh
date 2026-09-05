#!/usr/bin/env bash
# Prepare an arbitrary CUDA-capable NVIDIA pod and run Goal5844 end to end.

set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 EXPECTED_COMMIT OUTPUT_ROOT" >&2
  exit 2
fi

EXPECTED_COMMIT="$1"
OUTPUT_ROOT="$2"
REPO_ROOT="$(git rev-parse --show-toplevel)"
PYOPTIX_COMMIT="3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE="0bf0ec24efb4a43f129aee25dd265aa8149374e3"
UV_VERSION="0.12.10"
CURRENT_STAGE="initial_contract_validation"
OUTPUT_CREATED=0

stage() {
  CURRENT_STAGE="$1"
  printf '[Goal5844] stage=%s\n' "$CURRENT_STAGE" >&2
}

failure_bundle() {
  local return_code="$1"
  local line_number="$2"
  trap - ERR
  printf 'GOAL5844_FAILED stage=%s line=%s return_code=%s\n' \
    "$CURRENT_STAGE" "$line_number" "$return_code" >&2
  if [[ "$OUTPUT_CREATED" -eq 1 && -d "$OUTPUT_ROOT" ]]; then
    printf 'stage=%s\nline=%s\nreturn_code=%s\n' \
      "$CURRENT_STAGE" "$line_number" "$return_code" \
      > "$OUTPUT_ROOT/FAILED_STAGE.txt" || true
    local parent base
    parent="$(dirname "$OUTPUT_ROOT")"
    base="$(basename "$OUTPUT_ROOT")"
    tar --exclude="$base/venv" --exclude="$base/upstream" \
      --exclude="$base/build-home" --exclude="$base/tmp" \
      --exclude="$base/uv-bootstrap" --exclude="$base/uv-python" \
      --exclude="$base/uv-cache" \
      --exclude="$base/virtualenv-bootstrap" \
      --exclude="$base/preflight-cache" --exclude="$base/comparison-cache" \
      --exclude="$base/preflight-*-cache" \
      --exclude="$base/comparison-*-cache" \
      -czf "${OUTPUT_ROOT}.failure.tar.gz" -C "$parent" "$base" || true
    if [[ -f "${OUTPUT_ROOT}.failure.tar.gz" ]]; then
      sha256sum "${OUTPUT_ROOT}.failure.tar.gz" \
        > "${OUTPUT_ROOT}.failure.tar.gz.sha256" || true
      printf 'failure_archive=%s\n' "${OUTPUT_ROOT}.failure.tar.gz" >&2
    fi
  fi
  exit "$return_code"
}

abort() {
  local return_code="$1"
  shift
  printf '%s\n' "$*" >&2
  failure_bundle "$return_code" "${BASH_LINENO[0]}"
}

trap 'failure_bundle "$?" "$LINENO"' ERR

stage "validate_exact_git_checkout"
[[ "$EXPECTED_COMMIT" =~ ^[0-9a-f]{40}$ ]]
[[ "$OUTPUT_ROOT" = /* ]]
test "$(git -C "$REPO_ROOT" rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git -C "$REPO_ROOT" status --porcelain=v1 --untracked-files=all)"
test ! -e "$OUTPUT_ROOT"
mkdir -p \
  "$OUTPUT_ROOT/logs" "$OUTPUT_ROOT/upstream" \
  "$OUTPUT_ROOT/build-home" "$OUTPUT_ROOT/tmp"
OUTPUT_CREATED=1

export CUDA_VISIBLE_DEVICES=0
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PIP_CONFIG_FILE=/dev/null
export PIP_DISABLE_PIP_VERSION_CHECK=1
export HOME="$OUTPUT_ROOT/build-home"
export TMPDIR="$OUTPUT_ROOT/tmp"
SANITIZED_VARIABLES=(
  CFLAGS CPPFLAGS CXXFLAGS LDFLAGS LIBRARY_PATH CPATH CPLUS_INCLUDE_PATH
  CUDAFLAGS NVCC_PREPEND_FLAGS NVCC_APPEND_FLAGS CUDA_LAUNCH_BLOCKING
  CUDA_DEVICE_MAX_CONNECTIONS CUDA_CACHE_DISABLE CUDA_CACHE_MAXSIZE
  CUDA_CACHE_PATH CUPY_ACCELERATORS CUPY_CACHE_DIR NUMBA_CACHE_DIR
  XDG_CACHE_HOME CMAKE_GENERATOR CMAKE_TOOLCHAIN_FILE
)
for variable in "${SANITIZED_VARIABLES[@]}"; do
  unset "$variable"
done
printf '%s\n' "${SANITIZED_VARIABLES[@]}" \
  > "$OUTPUT_ROOT/logs/sanitized_environment_variables.txt"

stage "probe_and_repair_host_tools"
command -v nvidia-smi >/dev/null 2>&1 || {
  abort 20 "nvidia-smi is absent; no visible NVIDIA host runtime"
}
missing_host_tool=0
for command in git nm g++ tar sha256sum awk grep find sort cut xargs wc; do
  command -v "$command" >/dev/null 2>&1 || missing_host_tool=1
done
if [[ "$missing_host_tool" -eq 1 ]] && command -v apt-get >/dev/null 2>&1; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git build-essential binutils pkg-config libgeos-dev tar coreutils \
    findutils gawk grep
fi
for command in git nvidia-smi nm g++ tar sha256sum awk grep find sort cut xargs wc; do
  command -v "$command" >/dev/null 2>&1 || {
    abort 20 "missing required host command after repair: $command"
  }
done

GPU_ROW="$(nvidia-smi --id=0 --query-gpu=name,uuid,driver_version,compute_cap,memory.total --format=csv,noheader,nounits)"
test "$(printf '%s\n' "$GPU_ROW" | wc -l)" -eq 1
nvidia-smi -q -i 0 > "$OUTPUT_ROOT/logs/gpu_state_before.txt"
nvidia-smi --query-compute-apps=pid,process_name,used_memory \
  --format=csv,noheader,nounits \
  > "$OUTPUT_ROOT/logs/gpu_compute_processes_before.txt" || true
if [[ -s "$OUTPUT_ROOT/logs/gpu_compute_processes_before.txt" ]]; then
  abort 24 "visible GPU 0 already has active compute processes"
fi
DRIVER_VERSION="$(printf '%s' "$GPU_ROW" | cut -d, -f3 | xargs)"
COMPUTE_CAPABILITY="$(printf '%s' "$GPU_ROW" | cut -d, -f4 | xargs)"
COMPUTE_CODE="${COMPUTE_CAPABILITY/./}"

select_compatible_nvcc() {
  local candidate
  while IFS= read -r candidate; do
    [[ -n "$candidate" && -x "$candidate" ]] || continue
    if "$candidate" --list-gpu-code 2>/dev/null \
        | grep -qx "compute_${COMPUTE_CODE}"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done < <(
    {
      command -v nvcc 2>/dev/null || true
      find /usr/local -maxdepth 4 \( -type f -o -type l \) \
        -path '*/bin/nvcc' -perm -111 2>/dev/null || true
    } | awk '!seen[$0]++' | sort -Vr
  )
  return 1
}

stage "select_or_install_cuda_toolkit"
NVCC="$(select_compatible_nvcc || true)"
if [[ -z "$NVCC" ]]; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update
    for package in \
        cuda-toolkit-12-9 cuda-toolkit-12-8 cuda-toolkit-12-6 \
        cuda-toolkit-12-4 cuda-toolkit-12-2; do
      if apt-cache show "$package" 2>/dev/null | grep -q '^Package:'; then
        if DEBIAN_FRONTEND=noninteractive apt-get install -y "$package" \
            > "$OUTPUT_ROOT/logs/${package}_install.stdout" \
            2> "$OUTPUT_ROOT/logs/${package}_install.stderr"; then
          NVCC="$(select_compatible_nvcc || true)"
          [[ -n "$NVCC" ]] && break
        fi
      fi
    done
    [[ -n "$NVCC" ]] || NVCC="$(select_compatible_nvcc || true)"
  fi
fi
if [[ -z "$NVCC" ]]; then
  abort 21 \
    "no CUDA toolkit compiler supports compute_${COMPUTE_CODE} after repair"
fi
CUDA_ROOT="$(cd "$(dirname "$NVCC")/.." && pwd)"
test -x "$CUDA_ROOT/bin/nvcc"
test -f "$CUDA_ROOT/include/cuda.h"
export PATH="$CUDA_ROOT/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_ROOT/lib64:$CUDA_ROOT/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"

stage "create_isolated_python"
BASE_PYTHON=""
for candidate in python3.12 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1 \
      && "$candidate" -c 'import sys; raise SystemExit(sys.version_info[:2] not in {(3, 11), (3, 12)})'; then
    BASE_PYTHON="$(command -v "$candidate")"
    break
  fi
done
if [[ -z "$BASE_PYTHON" ]]; then
  BOOTSTRAP_PYTHON="$(command -v python3 || true)"
  if [[ -z "$BOOTSTRAP_PYTHON" ]] && command -v apt-get >/dev/null 2>&1; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip
    BOOTSTRAP_PYTHON="$(command -v python3 || true)"
  fi
  [[ -n "$BOOTSTRAP_PYTHON" ]] || \
    abort 22 "no Python is available to install the pinned Python 3.12 fallback"
  if ! "$BOOTSTRAP_PYTHON" -m pip --version >/dev/null 2>&1; then
    if ! "$BOOTSTRAP_PYTHON" -m ensurepip --upgrade \
        > "$OUTPUT_ROOT/logs/bootstrap_ensurepip.stdout" \
        2> "$OUTPUT_ROOT/logs/bootstrap_ensurepip.stderr"; then
      command -v apt-get >/dev/null 2>&1 || \
        abort 22 "bootstrap Python has neither pip nor ensurepip"
      apt-get update
      DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip
    fi
  fi
  "$BOOTSTRAP_PYTHON" -m pip install --no-deps \
    --target "$OUTPUT_ROOT/uv-bootstrap" \
    --report "$OUTPUT_ROOT/logs/uv_bootstrap_install_report.json" \
    "uv==$UV_VERSION" \
    > "$OUTPUT_ROOT/logs/uv_bootstrap_install.stdout" \
    2> "$OUTPUT_ROOT/logs/uv_bootstrap_install.stderr"
  UV_BIN="$OUTPUT_ROOT/uv-bootstrap/bin/uv"
  test -x "$UV_BIN"
  export UV_PYTHON_INSTALL_DIR="$OUTPUT_ROOT/uv-python"
  export UV_CACHE_DIR="$OUTPUT_ROOT/uv-cache"
  export UV_NO_PROGRESS=1
  "$UV_BIN" --version > "$OUTPUT_ROOT/logs/uv_version.txt"
  sha256sum "$UV_BIN" > "$OUTPUT_ROOT/logs/uv_binary.sha256"
  "$UV_BIN" python install 3.12 \
    > "$OUTPUT_ROOT/logs/uv_python_install.stdout" \
    2> "$OUTPUT_ROOT/logs/uv_python_install.stderr"
  BASE_PYTHON="$("$UV_BIN" python find 3.12)"
fi

if ! "$BASE_PYTHON" -m venv --copies "$OUTPUT_ROOT/venv"; then
  "$BASE_PYTHON" -m pip install --target "$OUTPUT_ROOT/virtualenv-bootstrap" \
    --report "$OUTPUT_ROOT/logs/virtualenv_bootstrap_install_report.json" \
    'virtualenv==20.35.4' 'distlib==0.4.0' \
    'filelock==3.19.1' 'platformdirs==4.4.0' \
    > "$OUTPUT_ROOT/logs/virtualenv_bootstrap_install.stdout" \
    2> "$OUTPUT_ROOT/logs/virtualenv_bootstrap_install.stderr"
  PYTHONPATH="$OUTPUT_ROOT/virtualenv-bootstrap" \
    "$BASE_PYTHON" -m virtualenv --copies "$OUTPUT_ROOT/venv"
fi
PYTHON="$OUTPUT_ROOT/venv/bin/python"
export PATH="$OUTPUT_ROOT/venv/bin:$PATH"
"$PYTHON" -m pip install --upgrade --no-deps \
  --report "$OUTPUT_ROOT/logs/pip_upgrade_install_report.json" \
  'pip==26.2.1' \
  > "$OUTPUT_ROOT/logs/pip_upgrade.stdout" \
  2> "$OUTPUT_ROOT/logs/pip_upgrade.stderr"
"$PYTHON" -m pip uninstall -y setuptools \
  > "$OUTPUT_ROOT/logs/setuptools_remove.stdout" \
  2> "$OUTPUT_ROOT/logs/setuptools_remove.stderr"
stage "install_and_record_pinned_dependencies"
"$PYTHON" -m pip install \
  --force-reinstall \
  --report "$OUTPUT_ROOT/logs/dependency_install_report.json" \
  'cmake==3.31.6' 'wheel==0.45.1' 'scikit-build-core==1.0.3' \
  'pybind11==3.1.0' 'ninja==1.13.0' \
  'packaging==26.3' 'pathspec==1.1.1' \
  'numpy==2.4.4' 'Pillow==10.2.0' 'numba==0.65.1' \
  'cuda-pathfinder==1.6.1' 'cuda-bindings==12.9.7' \
  'cuda-python==12.9.7' 'cupy-cuda12x==14.0.1' \
  'nvidia-ml-py==13.580.82' \
  > "$OUTPUT_ROOT/logs/dependency_install.stdout" \
  2> "$OUTPUT_ROOT/logs/dependency_install.stderr"

stage "select_driver_compatible_optix_stack"
SELECTOR="$REPO_ROOT/experiments/goal5798_premeasurement/compatibility.py"
OPTIX_API="$($PYTHON "$SELECTOR" --driver "$DRIVER_VERSION" --field optix_api_version)"
OPTIX_COMMIT="$($PYTHON "$SELECTOR" --driver "$DRIVER_VERSION" --field optix_header_commit)"
STACK_ID="$($PYTHON "$SELECTOR" --driver "$DRIVER_VERSION" --field stack_id)"

clone_exact() {
  local destination="$1"
  local remote="$2"
  local commit="$3"
  git init -q "$destination"
  git -C "$destination" remote add origin "$remote"
  git -C "$destination" fetch -q --depth 1 origin "$commit"
  git -C "$destination" checkout -q --detach FETCH_HEAD
  test "$(git -C "$destination" rev-parse HEAD)" = "$commit"
  test -z "$(git -C "$destination" status --porcelain=v1 --untracked-files=all)"
}

PYOPTIX_SOURCE="$OUTPUT_ROOT/upstream/otk-pyoptix"
OPTIX_HEADERS="$OUTPUT_ROOT/upstream/optix-dev"
stage "fetch_pinned_pyoptix_and_optix_headers"
clone_exact "$PYOPTIX_SOURCE" https://github.com/NVIDIA/otk-pyoptix.git "$PYOPTIX_COMMIT"
test "$(git -C "$PYOPTIX_SOURCE" rev-parse 'HEAD^{tree}')" = "$PYOPTIX_TREE"
clone_exact "$OPTIX_HEADERS" https://github.com/NVIDIA/optix-dev.git "$OPTIX_COMMIT"

export PYTHONPATH="$REPO_ROOT/src:$REPO_ROOT"
PYOPTIX_BUILD="$OUTPUT_ROOT/pyoptix-build"
stage "build_and_bind_clean_pyoptix_wheel"
"$PYTHON" "$REPO_ROOT/scripts/goal5844_build_install_pyoptix.py" \
  --python "$PYTHON" \
  --pyoptix-source "$PYOPTIX_SOURCE" \
  --optix-headers "$OPTIX_HEADERS" \
  --expected-optix-api "$OPTIX_API" \
  --dependency-install-report "$OUTPUT_ROOT/logs/dependency_install_report.json" \
  --output-root "$PYOPTIX_BUILD" \
  > "$OUTPUT_ROOT/logs/pyoptix_build.stdout" \
  2> "$OUTPUT_ROOT/logs/pyoptix_build.stderr"

NATIVE_ROOT="$OUTPUT_ROOT/native-build"
mkdir -p "$NATIVE_ROOT"
NATIVE="$NATIVE_ROOT/librtdl_optix.so"
NATIVE_MANIFEST="$NATIVE_ROOT/build_manifest.json"
stage "build_and_bind_rtdl_native_provider"
"$PYTHON" "$REPO_ROOT/scripts/goal5838_build_selected_sphere_optix_provider.py" \
  --cuda-prefix "$CUDA_ROOT" \
  --optix-prefix "$OPTIX_HEADERS" \
  --expected-optix-sdk "$OPTIX_API" \
  --compute-capability "$COMPUTE_CAPABILITY" \
  --expected-commit "$EXPECTED_COMMIT" \
  --output "$NATIVE" \
  --manifest "$NATIVE_MANIFEST" \
  --log "$NATIVE_ROOT/build.log" \
  > "$OUTPUT_ROOT/logs/rtdl_native_build.stdout" \
  2> "$OUTPUT_ROOT/logs/rtdl_native_build.stderr"
nm -D --defined-only "$NATIVE" | grep -q \
  'rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v8$'

stage "run_focused_contract_tests"
"$PYTHON" -m unittest -v \
  tests.goal5844_compact_execution_stamp_test \
  tests.goal5844_pre_pod_readiness_test \
  > "$OUTPUT_ROOT/logs/focused_tests.stdout" \
  2> "$OUTPUT_ROOT/logs/focused_tests.stderr"

DEVICE_SOURCE="$REPO_ROOT/experiments/goal5796_matched/matched_device.cu"
COMMON=(
  --native "$NATIVE"
  --device-source "$DEVICE_SOURCE"
  --optix-include "$OPTIX_HEADERS/include"
  --cuda-include "$CUDA_ROOT/include"
  --optix-sdk "$OPTIX_API"
  --compute-capability "$COMPUTE_CAPABILITY"
  --pyoptix-source "$PYOPTIX_SOURCE"
  --pyoptix-build-receipt "$PYOPTIX_BUILD/build_receipt.json"
  --warmups 1 --repetitions 1 --layer-warmups 1 --layer-repetitions 1
)
PREFLIGHT="$OUTPUT_ROOT/preflight"
mkdir -p "$PREFLIGHT"
stage "run_untimed_two_arm_preflight"
export CUDA_CACHE_PATH="$OUTPUT_ROOT/preflight-cuda-cache"
export CUPY_CACHE_DIR="$OUTPUT_ROOT/preflight-cupy-cache"
export NUMBA_CACHE_DIR="$OUTPUT_ROOT/preflight-numba-cache"
export XDG_CACHE_HOME="$OUTPUT_ROOT/preflight-xdg-cache"
test ! -e "$CUDA_CACHE_PATH"
test ! -e "$CUPY_CACHE_DIR"
test ! -e "$NUMBA_CACHE_DIR"
test ! -e "$XDG_CACHE_HOME"
"$PYTHON" -m experiments.goal5844_compact_execution.worker \
  --arm RTDL_PUBLIC_V8_COMPACT_STAMP --block 0 \
  --cache-root "$OUTPUT_ROOT/preflight-cache" \
  --output "$PREFLIGHT/rtdl.json" "${COMMON[@]}" \
  > "$PREFLIGHT/rtdl.stdout" 2> "$PREFLIGHT/rtdl.stderr"
"$PYTHON" -m experiments.goal5844_compact_execution.worker \
  --arm PINNED_PYOPTIX_COMPATIBLE_API --block 0 \
  --cache-root "$OUTPUT_ROOT/preflight-cache" \
  --output "$PREFLIGHT/pyoptix.json" "${COMMON[@]}" \
  > "$PREFLIGHT/pyoptix.stdout" 2> "$PREFLIGHT/pyoptix.stderr"

COMPARISON_ROOT="$OUTPUT_ROOT/comparison"
COMPARISON_CACHE="$OUTPUT_ROOT/comparison-cache"
stage "run_balanced_fresh_cache_engineering_comparison"
export CUDA_CACHE_PATH="$OUTPUT_ROOT/comparison-cuda-cache"
export CUPY_CACHE_DIR="$OUTPUT_ROOT/comparison-cupy-cache"
export NUMBA_CACHE_DIR="$OUTPUT_ROOT/comparison-numba-cache"
export XDG_CACHE_HOME="$OUTPUT_ROOT/comparison-xdg-cache"
test ! -e "$CUDA_CACHE_PATH"
test ! -e "$CUPY_CACHE_DIR"
test ! -e "$NUMBA_CACHE_DIR"
test ! -e "$XDG_CACHE_HOME"
"$PYTHON" "$REPO_ROOT/scripts/goal5844_run_gpu_engineering_comparison.py" \
  --python "$PYTHON" \
  --native "$NATIVE" \
  --native-build-manifest "$NATIVE_MANIFEST" \
  --device-source "$DEVICE_SOURCE" \
  --optix-include "$OPTIX_HEADERS/include" \
  --cuda-include "$CUDA_ROOT/include" \
  --optix-sdk "$OPTIX_API" \
  --compute-capability "$COMPUTE_CAPABILITY" \
  --cache-root "$COMPARISON_CACHE" \
  --pyoptix-source "$PYOPTIX_SOURCE" \
  --pyoptix-build-receipt "$PYOPTIX_BUILD/build_receipt.json" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --blocks "${GOAL5844_BLOCKS:-8}" \
  --warmups "${GOAL5844_WARMUPS:-16}" \
  --repetitions "${GOAL5844_REPETITIONS:-128}" \
  --layer-warmups "${GOAL5844_LAYER_WARMUPS:-8}" \
  --layer-repetitions "${GOAL5844_LAYER_REPETITIONS:-64}" \
  --output-root "$COMPARISON_ROOT" \
  > "$OUTPUT_ROOT/logs/comparison.stdout" \
  2> "$OUTPUT_ROOT/logs/comparison.stderr"

stage "reverify_complete_result_on_pod"
"$PYTHON" "$REPO_ROOT/scripts/goal5844_verify_gpu_engineering_result.py" \
  --result-root "$COMPARISON_ROOT" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --output "$OUTPUT_ROOT/DOWNLOADED_STYLE_VERIFICATION.json" \
  > "$OUTPUT_ROOT/logs/result_verification.stdout" \
  2> "$OUTPUT_ROOT/logs/result_verification.stderr"
nvidia-smi -q -i 0 > "$OUTPUT_ROOT/logs/gpu_state_after.txt"
nvidia-smi --query-compute-apps=pid,process_name,used_memory \
  --format=csv,noheader,nounits \
  > "$OUTPUT_ROOT/logs/gpu_compute_processes_after.txt" || true
if [[ -s "$OUTPUT_ROOT/logs/gpu_compute_processes_after.txt" ]]; then
  abort 24 "Goal5844 left active compute processes on visible GPU 0"
fi

"$PYTHON" - "$OUTPUT_ROOT" "$EXPECTED_COMMIT" "$GPU_ROW" "$STACK_ID" \
    "$OPTIX_API" "$CUDA_ROOT" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
summary = root / "comparison" / "SUMMARY.json"
value = {
    "schema": "rtdl.goal5844.pod_transaction.v1",
    "status": "PASS__PREPARE_PREFLIGHT_COMPARE_AND_REVERIFY_COMPLETE",
    "source_commit": sys.argv[2],
    "gpu_identity_row": sys.argv[3],
    "selected_stack_id": sys.argv[4],
    "selected_optix_api": sys.argv[5],
    "cuda_root": sys.argv[6],
    "comparison_summary_sha256": hashlib.sha256(summary.read_bytes()).hexdigest(),
    "claim_boundary": {
        "internal_engineering_evidence_only": True,
        "public_or_manuscript_claim_authorized": False,
        "external_review_complete": False,
    },
}
body = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
value["transaction_sha256"] = hashlib.sha256(body).hexdigest()
(root / "POD_TRANSACTION.json").write_text(
    json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
PY

stage "package_return_evidence"
ARCHIVE="${OUTPUT_ROOT}.tar.gz"
test ! -e "$ARCHIVE"
tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
  -czf "$ARCHIVE" -C "$OUTPUT_ROOT" \
  logs preflight comparison DOWNLOADED_STYLE_VERIFICATION.json POD_TRANSACTION.json
sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256"
trap - ERR
printf 'GOAL5844_COMPLETE\narchive=%s\nsha256_file=%s\n' "$ARCHIVE" "${ARCHIVE}.sha256"
