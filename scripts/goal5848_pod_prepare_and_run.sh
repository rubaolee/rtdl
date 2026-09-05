#!/usr/bin/env bash
# Prepare one arbitrary NVIDIA pod and execute one Goal5848 generation once.

set -euo pipefail

if [[ "$#" -lt 2 || "$#" -gt 3 ]]; then
  echo "usage: $0 EXPECTED_COMMIT OUTPUT_ROOT [PREDECESSOR_COMMIT]" >&2
  exit 2
fi

EXPECTED_COMMIT="$1"
OUTPUT_ROOT="$2"
PREDECESSOR_COMMIT="${3:-12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8}"
PYOPTIX_COMMIT="3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE="0bf0ec24efb4a43f129aee25dd265aa8149374e3"
UV_VERSION="0.12.10"
REPO_ROOT="$(cd "$(git rev-parse --show-toplevel)" && pwd -P)"
CURRENT_STAGE="initial_contract_validation"
OUTPUT_CREATED=0
PREDECESSOR_WORKTREE_CREATED=0

stage() {
  CURRENT_STAGE="$1"
  printf '[Goal5848] stage=%s\n' "$CURRENT_STAGE" >&2
}

failure_bundle() {
  local return_code="$1"
  local line_number="$2"
  trap - ERR
  printf 'GOAL5848_FAILED stage=%s line=%s return_code=%s\n' \
    "$CURRENT_STAGE" "$line_number" "$return_code" >&2
  if [[ "$OUTPUT_CREATED" -eq 1 && -d "$OUTPUT_ROOT" ]]; then
    printf 'stage=%s\nline=%s\nreturn_code=%s\nretry_count=0\ndiscard_count=0\n' \
      "$CURRENT_STAGE" "$line_number" "$return_code" \
      > "$OUTPUT_ROOT/FAILED_STAGE.txt" || true
    local parent base
    parent="$(dirname "$OUTPUT_ROOT")"
    base="$(basename "$OUTPUT_ROOT")"
    tar \
      --exclude="$base/venv" \
      --exclude="$base/upstream" \
      --exclude="$base/predecessor-source" \
      --exclude="$base/build-home" \
      --exclude="$base/tmp" \
      --exclude="$base/uv-bootstrap" \
      --exclude="$base/uv-python" \
      --exclude="$base/uv-cache" \
      --exclude="$base/virtualenv-bootstrap" \
      --exclude="$base/current-leaf-cache" \
      --exclude="$base/predecessor-leaf-cache" \
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
[[ "$PREDECESSOR_COMMIT" =~ ^[0-9a-f]{40}$ ]]
[[ "$OUTPUT_ROOT" = /* ]]
OUTPUT_PARENT="$(dirname "$OUTPUT_ROOT")"
test -d "$OUTPUT_PARENT"
OUTPUT_PARENT="$(cd "$OUTPUT_PARENT" && pwd -P)"
OUTPUT_BASENAME="$(basename "$OUTPUT_ROOT")"
[[ "$OUTPUT_BASENAME" != "." && "$OUTPUT_BASENAME" != ".." ]]
OUTPUT_ROOT="$OUTPUT_PARENT/$OUTPUT_BASENAME"
case "$OUTPUT_ROOT/" in
  "$REPO_ROOT/"*) abort 2 "OUTPUT_ROOT must be outside the Git checkout" ;;
esac
test "$(git -C "$REPO_ROOT" rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git -C "$REPO_ROOT" status --porcelain=v1 --untracked-files=all)"
test ! -e "$OUTPUT_ROOT"
mkdir -p \
  "$OUTPUT_ROOT/logs" \
  "$OUTPUT_ROOT/environment" \
  "$OUTPUT_ROOT/upstream" \
  "$OUTPUT_ROOT/build-home" \
  "$OUTPUT_ROOT/tmp"
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
  CUDA_DEVICE_MAX_CONNECTIONS CUDA_CACHE_MAXSIZE CUDA_CACHE_PATH
  CUDA_MODULE_LOADING CUDA_FORCE_PTX_JIT CUDA_DISABLE_PTX_JIT
  CUDA_INJECTION64_PATH CUDA_INJECTION32_PATH CUDA_DEVICE_ORDER CUDA_AUTO_BOOST
  CUPY_ACCELERATORS CUPY_CACHE_DIR CUPY_CACHE_IN_MEMORY
  NUMBA_CACHE_DIR NUMBA_ENABLE_CUDASIM NUMBA_FORCE_CUDA_CC
  NUMBA_CUDA_DEFAULT_PTX_CC XDG_CACHE_HOME
  CMAKE_GENERATOR CMAKE_TOOLCHAIN_FILE RTDL_GOAL5807_PROFILE_NATIVE
  LD_PRELOAD PYTHONHOME PYTHONINSPECT PYTHONSTARTUP PYTHONHASHSEED
  OMP_NUM_THREADS OPENBLAS_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS
  VECLIB_MAXIMUM_THREADS BLIS_NUM_THREADS
  RTDL_OPTIX_DISK_CACHE_POLICY
)
for variable in "${SANITIZED_VARIABLES[@]}"; do
  unset "$variable"
done
export CUDA_CACHE_DISABLE=1
export RTDL_OPTIX_DISK_CACHE_POLICY=disabled
printf '%s\n' "${SANITIZED_VARIABLES[@]}" \
  > "$OUTPUT_ROOT/environment/sanitized_environment_variables.txt"
printf 'CUDA_CACHE_DISABLE=1\nRTDL_OPTIX_DISK_CACHE_POLICY=disabled\n' \
  > "$OUTPUT_ROOT/environment/formal_cache_policy.txt"

stage "probe_and_repair_host_tools"
command -v nvidia-smi >/dev/null 2>&1 || {
  abort 20 "nvidia-smi is absent; no visible NVIDIA host runtime"
}
missing_host_tool=0
for command in git nm g++ tar gzip sha256sum awk grep find sort cut xargs wc cmp; do
  command -v "$command" >/dev/null 2>&1 || missing_host_tool=1
done
if [[ "$missing_host_tool" -eq 1 ]] && command -v apt-get >/dev/null 2>&1; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git build-essential binutils pkg-config libgeos-dev tar gzip coreutils \
    findutils gawk grep
fi
for command in git nvidia-smi nm g++ tar gzip sha256sum awk grep find sort cut xargs wc cmp; do
  command -v "$command" >/dev/null 2>&1 || {
    abort 20 "missing required host command after repair: $command"
  }
done

GPU_ROW="$(nvidia-smi --id=0 --query-gpu=name,uuid,driver_version,compute_cap,memory.total --format=csv,noheader,nounits)"
test "$(printf '%s\n' "$GPU_ROW" | wc -l)" -eq 1
printf '%s\n' "$GPU_ROW" > "$OUTPUT_ROOT/environment/gpu_identity.csv"
nvidia-smi -q -i 0 > "$OUTPUT_ROOT/environment/gpu_state_before.txt"
nvidia-smi --query-compute-apps=pid,process_name,used_memory \
  --format=csv,noheader,nounits \
  > "$OUTPUT_ROOT/environment/gpu_compute_processes_before.txt" || true
if [[ -s "$OUTPUT_ROOT/environment/gpu_compute_processes_before.txt" ]]; then
  abort 24 "visible GPU 0 already has active compute processes"
fi
DRIVER_VERSION="$(printf '%s' "$GPU_ROW" | cut -d, -f3 | xargs)"
COMPUTE_CAPABILITY="$(printf '%s' "$GPU_ROW" | cut -d, -f4 | xargs)"
COMPUTE_CODE="${COMPUTE_CAPABILITY/./}"
case "$COMPUTE_CAPABILITY" in
  7.5|8.6|8.9|12.0) ;;
  *) abort 25 "GPU is not a preregistered Goal5848 RTX architecture" ;;
esac

select_compatible_nvcc() {
  local candidate
  while IFS= read -r candidate; do
    [[ -n "$candidate" && -x "$candidate" ]] || continue
    if "$candidate" --list-gpu-code 2>/dev/null \
        | grep -Eq "^(compute|sm)_${COMPUTE_CODE}$"; then
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
if [[ -z "$NVCC" ]] && command -v apt-get >/dev/null 2>&1; then
  apt-get update
  for package in \
      cuda-toolkit-13-0 cuda-toolkit-12-9 cuda-toolkit-12-8 \
      cuda-toolkit-12-6 cuda-toolkit-12-4 cuda-toolkit-12-2; do
    if apt-cache show "$package" 2>/dev/null | grep -q '^Package:'; then
      if DEBIAN_FRONTEND=noninteractive apt-get install -y "$package" \
          > "$OUTPUT_ROOT/logs/${package}_install.stdout" \
          2> "$OUTPUT_ROOT/logs/${package}_install.stderr"; then
        NVCC="$(select_compatible_nvcc || true)"
        [[ -n "$NVCC" ]] && break
      fi
    fi
  done
fi
if [[ -z "$NVCC" ]]; then
  abort 21 "no CUDA toolkit compiler supports compute_${COMPUTE_CODE} after repair"
fi
CUDA_ROOT="$(cd "$(dirname "$NVCC")/.." && pwd)"
test -x "$CUDA_ROOT/bin/nvcc"
test -f "$CUDA_ROOT/include/cuda.h"
CUDA_TOOLKIT_VERSION="$("$NVCC" --version | sed -n 's/.*release \([0-9][0-9.]*\),.*/\1/p' | tail -1)"
test -n "$CUDA_TOOLKIT_VERSION"
export PATH="$CUDA_ROOT/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_ROOT/lib64:$CUDA_ROOT/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
"$NVCC" --version > "$OUTPUT_ROOT/environment/nvcc_version.txt"
printf '%s\n' "$CUDA_ROOT" > "$OUTPUT_ROOT/environment/cuda_root.txt"
NVRTC_LIBRARY="$(find "$CUDA_ROOT" -type f -name 'libnvrtc.so*' 2>/dev/null | sort -V | tail -1)"
test -n "$NVRTC_LIBRARY"
NVRTC_LIBRARY="$(readlink -f "$NVRTC_LIBRARY")"
test -f "$NVRTC_LIBRARY"

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
    abort 22 "no Python is available for the pinned Python fallback"
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
"$PYTHON" -m pip install --force-reinstall \
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
"$PYTHON" -m pip freeze --all > "$OUTPUT_ROOT/environment/pip_freeze.txt"
"$PYTHON" --version > "$OUTPUT_ROOT/environment/python_version.txt" 2>&1

stage "select_driver_compatible_optix_stack"
SELECTOR="$REPO_ROOT/experiments/goal5798_premeasurement/compatibility.py"
OPTIX_API="$("$PYTHON" "$SELECTOR" --driver "$DRIVER_VERSION" --field optix_api_version)"
OPTIX_COMMIT="$("$PYTHON" "$SELECTOR" --driver "$DRIVER_VERSION" --field optix_header_commit)"
STACK_ID="$("$PYTHON" "$SELECTOR" --driver "$DRIVER_VERSION" --field stack_id)"

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
OPTIX_TREE="$(git -C "$OPTIX_HEADERS" rev-parse 'HEAD^{tree}')"
printf '%s\n' "$STACK_ID" > "$OUTPUT_ROOT/environment/optix_stack_id.txt"
printf '%s\n' "$OPTIX_API" > "$OUTPUT_ROOT/environment/optix_api.txt"
printf '%s\n' "$OPTIX_COMMIT" > "$OUTPUT_ROOT/environment/optix_headers_commit.txt"

stage "materialize_exact_predecessor_worktree"
if ! git -C "$REPO_ROOT" cat-file -e "${PREDECESSOR_COMMIT}^{commit}" 2>/dev/null; then
  git -C "$REPO_ROOT" fetch -q origin "$PREDECESSOR_COMMIT"
fi
PREDECESSOR_ROOT="$OUTPUT_ROOT/predecessor-source"
git -C "$REPO_ROOT" worktree add -q --detach "$PREDECESSOR_ROOT" "$PREDECESSOR_COMMIT"
PREDECESSOR_WORKTREE_CREATED=1
test "$(git -C "$PREDECESSOR_ROOT" rev-parse HEAD)" = "$PREDECESSOR_COMMIT"
test -z "$(git -C "$PREDECESSOR_ROOT" status --porcelain=v1 --untracked-files=all)"

export PYTHONPATH="$REPO_ROOT/src:$REPO_ROOT"
stage "build_and_bind_clean_pyoptix_wheel"
PYOPTIX_BUILD="$OUTPUT_ROOT/pyoptix-build"
"$PYTHON" "$REPO_ROOT/scripts/goal5844_build_install_pyoptix.py" \
  --python "$PYTHON" \
  --pyoptix-source "$PYOPTIX_SOURCE" \
  --optix-headers "$OPTIX_HEADERS" \
  --expected-optix-api "$OPTIX_API" \
  --dependency-install-report "$OUTPUT_ROOT/logs/dependency_install_report.json" \
  --output-root "$PYOPTIX_BUILD" \
  > "$OUTPUT_ROOT/logs/pyoptix_build.stdout" \
  2> "$OUTPUT_ROOT/logs/pyoptix_build.stderr"

stage "run_local_contract_suite_before_gpu_build"
mapfile -t GOAL5848_TESTS < <(
  find "$REPO_ROOT/tests" -maxdepth 1 -type f -name 'goal5848_*_test.py' \
    -printf '%f\n' | sort | sed 's/\.py$//;s#^#tests.#'
)
"$PYTHON" -m unittest "${GOAL5848_TESTS[@]}" \
  > "$OUTPUT_ROOT/logs/goal5848_tests.stdout" \
  2> "$OUTPUT_ROOT/logs/goal5848_tests.stderr"

build_native() {
  local source_root="$1"
  local output_dir="$2"
  local expected="$3"
  mkdir -p "$output_dir"
  PYTHONPATH="$source_root/src:$source_root" \
    "$PYTHON" "$source_root/scripts/build_v4_optix_native_snapshot.py" \
      --cuda-prefix "$CUDA_ROOT" \
      --optix-prefix "$OPTIX_HEADERS" \
      --expected-optix-sdk "$OPTIX_API" \
      --compute-capability "$COMPUTE_CAPABILITY" \
      --host-compiler "$(command -v g++)" \
      --rtdlexe-aot-runtime \
      --output "$output_dir/librtdl_optix.so" \
      --manifest "$output_dir/build_manifest.json" \
      --log "$output_dir/build.log" \
      > "$output_dir/build.stdout" \
      2> "$output_dir/build.stderr"
  test "$(git -C "$source_root" rev-parse HEAD)" = "$expected"
  test -z "$(git -C "$source_root" status --porcelain=v1 --untracked-files=all)"
}

stage "build_current_minimal_aot_native"
CURRENT_NATIVE_ROOT="$OUTPUT_ROOT/current-native"
build_native "$REPO_ROOT" "$CURRENT_NATIVE_ROOT" "$EXPECTED_COMMIT"

stage "build_exact_goal5847_predecessor_native"
PREDECESSOR_NATIVE_ROOT="$OUTPUT_ROOT/predecessor-native"
build_native "$PREDECESSOR_ROOT" "$PREDECESSOR_NATIVE_ROOT" "$PREDECESSOR_COMMIT"

stage "build_direct_optix_lower_bound"
DIRECT_ROOT="$OUTPUT_ROOT/direct"
mkdir -p "$DIRECT_ROOT"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_render_direct_worker.py" \
  --output "$DIRECT_ROOT/direct_worker.cpp" \
  --receipt "$DIRECT_ROOT/derivation_receipt.json" \
  > "$OUTPUT_ROOT/logs/direct_render.stdout" \
  2> "$OUTPUT_ROOT/logs/direct_render.stderr"
DIRECT_RECIPE_ARGS=(
  --library-directory "$CUDA_ROOT/lib64"
)
if [[ -d "$CUDA_ROOT/targets/x86_64-linux/lib" ]]; then
  DIRECT_RECIPE_ARGS+=(
    --library-directory "$CUDA_ROOT/targets/x86_64-linux/lib"
  )
fi
"$PYTHON" "$REPO_ROOT/scripts/goal5802_build_direct_recipe.py" \
  "${DIRECT_RECIPE_ARGS[@]}" \
  --output "$DIRECT_ROOT/build_recipe.json" \
  > "$OUTPUT_ROOT/logs/direct_recipe.stdout" \
  2> "$OUTPUT_ROOT/logs/direct_recipe.stderr"
"$PYTHON" "$REPO_ROOT/scripts/goal5802_build_direct_worker_untimed.py" \
  --recipe "$DIRECT_ROOT/build_recipe.json" \
  --cxx "$(command -v g++)" \
  --direct-source "$DIRECT_ROOT/direct_worker.cpp" \
  --optix-include "$OPTIX_HEADERS/include" \
  --cuda-include "$CUDA_ROOT/include" \
  --output "$DIRECT_ROOT/direct_worker" \
  --receipt "$DIRECT_ROOT/build_receipt.json" \
  > "$OUTPUT_ROOT/logs/direct_build.stdout" \
  2> "$OUTPUT_ROOT/logs/direct_build.stderr"

stage "build_and_seal_shared_device_artifacts"
DEVICE_ARTIFACT_ROOT="$OUTPUT_ROOT/device-artifacts"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_build_device_artifacts.py" \
  --python "$PYTHON" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --optix-source "$OPTIX_HEADERS" \
  --expected-optix-commit "$OPTIX_COMMIT" \
  --expected-optix-tree "$OPTIX_TREE" \
  --expected-optix-sdk "$OPTIX_API" \
  --optix-include "$OPTIX_HEADERS/include" \
  --cuda-include "$CUDA_ROOT/include" \
  --compute-capability "$COMPUTE_CAPABILITY" \
  --nvrtc-library "$NVRTC_LIBRARY" \
  --output-root "$DEVICE_ARTIFACT_ROOT" \
  > "$OUTPUT_ROOT/logs/device_artifact_build.stdout" \
  2> "$OUTPUT_ROOT/logs/device_artifact_build.stderr"

stage "create_test_only_signing_roots"
SIGNING_ROOT="$OUTPUT_ROOT/signing-roots"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_create_test_signing_roots.py" \
  --output-root "$SIGNING_ROOT" \
  > "$OUTPUT_ROOT/logs/signing_roots.stdout" \
  2> "$OUTPUT_ROOT/logs/signing_roots.stderr"

stage "build_current_exact_aot_candidates"
CURRENT_AOT="$OUTPUT_ROOT/current-aot"
CURRENT_AOT_CACHE="$OUTPUT_ROOT/current-aot-cache"
CURRENT_LEAF_CACHE="$OUTPUT_ROOT/current-leaf-cache"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_build_aot_candidates.py" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --native "$CURRENT_NATIVE_ROOT/librtdl_optix.so" \
  --native-build-manifest "$CURRENT_NATIVE_ROOT/build_manifest.json" \
  --optix-include "$OPTIX_HEADERS/include" \
  --cuda-include "$CUDA_ROOT/include" \
  --optix-sdk "$OPTIX_API" \
  --compute-capability "$COMPUTE_CAPABILITY" \
  --cuda-toolkit-version "$CUDA_TOOLKIT_VERSION" \
  --leaf-cache-root "$CURRENT_LEAF_CACHE" \
  --aot-cache-root "$CURRENT_AOT_CACHE" \
  --relation-signing-private "$SIGNING_ROOT/relation.private.json" \
  --relation-signing-public "$SIGNING_ROOT/relation.public.json" \
  --triangle-signing-private "$SIGNING_ROOT/triangle.private.json" \
  --triangle-signing-public "$SIGNING_ROOT/triangle.public.json" \
  --signing-roots-receipt "$SIGNING_ROOT/receipt.json" \
  --unlink-signing-private-after-build \
  --output-root "$CURRENT_AOT" \
  --hit-repetitions 5 \
  --require-cold-first \
  > "$OUTPUT_ROOT/logs/current_aot_build.stdout" \
  2> "$OUTPUT_ROOT/logs/current_aot_build.stderr"
test ! -e "$SIGNING_ROOT/relation.private.json"
test ! -e "$SIGNING_ROOT/triangle.private.json"

stage "build_exact_goal5847_predecessor_candidates"
PREDECESSOR_CANDIDATES="$OUTPUT_ROOT/predecessor-candidates"
PREDECESSOR_LEAF_CACHE="$OUTPUT_ROOT/predecessor-leaf-cache"
PYTHONPATH="$PREDECESSOR_ROOT/src:$PREDECESSOR_ROOT" \
  "$PYTHON" "$PREDECESSOR_ROOT/scripts/goal5847_build_aot_candidates.py" \
    --expected-source-commit "$PREDECESSOR_COMMIT" \
    --native "$PREDECESSOR_NATIVE_ROOT/librtdl_optix.so" \
    --native-build-manifest "$PREDECESSOR_NATIVE_ROOT/build_manifest.json" \
    --optix-include "$OPTIX_HEADERS/include" \
    --cuda-include "$CUDA_ROOT/include" \
    --optix-sdk "$OPTIX_API" \
    --compute-capability "$COMPUTE_CAPABILITY" \
    --cuda-toolkit-version "$CUDA_TOOLKIT_VERSION" \
    --cache-root "$PREDECESSOR_LEAF_CACHE" \
    --output-root "$PREDECESSOR_CANDIDATES" \
    > "$OUTPUT_ROOT/logs/predecessor_aot_build.stdout" \
    2> "$OUTPUT_ROOT/logs/predecessor_aot_build.stderr"

stage "qualify_fresh_process_exact_aot_hits"
AOT_HIT_ROOT="$OUTPUT_ROOT/aot-hit"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_probe_aot_cache_hits.py" \
  --python "$PYTHON" \
  --candidate-manifest "$CURRENT_AOT/manifest.json" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --repetitions 5 \
  --output-root "$AOT_HIT_ROOT" \
  > "$OUTPUT_ROOT/logs/aot_hit.stdout" \
  2> "$OUTPUT_ROOT/logs/aot_hit.stderr"

PREREGISTRATION="$OUTPUT_ROOT/preregistration.json"
COMMON_ARTIFACT_ARGUMENTS=(
  --python "$PYTHON"
  --expected-source-commit "$EXPECTED_COMMIT"
  --predecessor-root "$PREDECESSOR_ROOT"
  --expected-predecessor-commit "$PREDECESSOR_COMMIT"
  --pyoptix-source "$PYOPTIX_SOURCE"
  --expected-pyoptix-commit "$PYOPTIX_COMMIT"
  --expected-pyoptix-tree "$PYOPTIX_TREE"
  --expected-optix-sdk "$OPTIX_API"
  --candidate-manifest "$CURRENT_AOT/manifest.json"
  --predecessor-candidate-manifest "$PREDECESSOR_CANDIDATES/manifest.json"
  --precompiled-ptx "$DEVICE_ARTIFACT_ROOT/matched_device.ptx"
  --compaction-cubin "$DEVICE_ARTIFACT_ROOT/relation_semantic_compaction.cubin"
  --device-artifact-build-receipt "$DEVICE_ARTIFACT_ROOT/device_artifact_build_receipt.json"
  --pyoptix-build-receipt "$PYOPTIX_BUILD/build_receipt.json"
  --direct-worker "$DIRECT_ROOT/direct_worker"
  --direct-build-receipt "$DIRECT_ROOT/build_receipt.json"
  --derivation-receipt "$DIRECT_ROOT/derivation_receipt.json"
  --aot-cache-authority "$AOT_HIT_ROOT/authority.json"
)

stage "freeze_formal_preregistration"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_freeze_preregistration.py" \
  "${COMMON_ARTIFACT_ARGUMENTS[@]}" \
  --output "$PREREGISTRATION" \
  > "$OUTPUT_ROOT/logs/preregistration.stdout" \
  2> "$OUTPUT_ROOT/logs/preregistration.stderr"

COMMON_FORMAL_ARGUMENTS=(
  "${COMMON_ARTIFACT_ARGUMENTS[@]}"
  --preregistration "$PREREGISTRATION"
)

stage "run_timer_free_eight_arm_task_witnesses"
TIMER_FREE_ROOT="$OUTPUT_ROOT/timer-free-witness"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_run_timer_free_preflight.py" \
  "${COMMON_FORMAL_ARGUMENTS[@]}" \
  --output-root "$TIMER_FREE_ROOT" \
  > "$OUTPUT_ROOT/logs/timer_free_preflight.stdout" \
  2> "$OUTPUT_ROOT/logs/timer_free_preflight.stderr"

stage "run_nonformal_baseline_competence_gate"
COMPETENCE_ROOT="$OUTPUT_ROOT/baseline-competence"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_run_baseline_competence.py" \
  "${COMMON_FORMAL_ARGUMENTS[@]}" \
  --output-root "$COMPETENCE_ROOT" \
  > "$OUTPUT_ROOT/logs/baseline_competence.stdout" \
  2> "$OUTPUT_ROOT/logs/baseline_competence.stderr"

stage "run_paired_instrumentation_overhead_gate"
INSTRUMENTATION_ROOT="$OUTPUT_ROOT/instrumentation-overhead"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_run_instrumentation_overhead.py" \
  --python "$PYTHON" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --expected-predecessor-commit "$PREDECESSOR_COMMIT" \
  --preregistration "$PREREGISTRATION" \
  --candidate-manifest "$CURRENT_AOT/manifest.json" \
  --output-root "$INSTRUMENTATION_ROOT" \
  > "$OUTPUT_ROOT/logs/instrumentation_overhead.stdout" \
  2> "$OUTPUT_ROOT/logs/instrumentation_overhead.stderr"

stage "finalize_preflight_authority"
FINAL_PREFLIGHT="$OUTPUT_ROOT/preflight.json"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_finalize_preflight.py" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --expected-predecessor-commit "$PREDECESSOR_COMMIT" \
  --preregistration "$PREREGISTRATION" \
  --timer-free-witness "$TIMER_FREE_ROOT/authority.json" \
  --baseline-competence "$COMPETENCE_ROOT/authority.json" \
  --instrumentation-overhead "$INSTRUMENTATION_ROOT/authority.json" \
  --output "$FINAL_PREFLIGHT" \
  > "$OUTPUT_ROOT/logs/finalize_preflight.stdout" \
  2> "$OUTPUT_ROOT/logs/finalize_preflight.stderr"

stage "run_single_attempt_eighty_cell_formal_transaction"
FORMAL_ROOT="$OUTPUT_ROOT/formal-transaction"
"$PYTHON" -m experiments.goal5848_strong_baseline.controller \
  "${COMMON_FORMAL_ARGUMENTS[@]}" \
  --preflight "$FINAL_PREFLIGHT" \
  --output-root "$FORMAL_ROOT" \
  > "$OUTPUT_ROOT/logs/formal_transaction.stdout" \
  2> "$OUTPUT_ROOT/logs/formal_transaction.stderr"

stage "build_independent_single_generation_authority"
SINGLE_AUTHORITY="$OUTPUT_ROOT/single-generation-authority.json"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_build_transaction_authority.py" \
  --transaction-root "$FORMAL_ROOT" \
  --preregistration "$PREREGISTRATION" \
  --preflight "$FINAL_PREFLIGHT" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --expected-predecessor-commit "$PREDECESSOR_COMMIT" \
  --output "$SINGLE_AUTHORITY" \
  > "$OUTPUT_ROOT/logs/single_generation_authority.stdout" \
  2> "$OUTPUT_ROOT/logs/single_generation_authority.stderr"

stage "rebuild_and_compare_single_generation_authority"
SINGLE_AUTHORITY_RECOUNT="$OUTPUT_ROOT/single-generation-authority.recount.json"
"$PYTHON" "$REPO_ROOT/scripts/goal5848_build_transaction_authority.py" \
  --transaction-root "$FORMAL_ROOT" \
  --preregistration "$PREREGISTRATION" \
  --preflight "$FINAL_PREFLIGHT" \
  --expected-source-commit "$EXPECTED_COMMIT" \
  --expected-predecessor-commit "$PREDECESSOR_COMMIT" \
  --output "$SINGLE_AUTHORITY_RECOUNT" \
  > "$OUTPUT_ROOT/logs/single_generation_authority_recount.stdout" \
  2> "$OUTPUT_ROOT/logs/single_generation_authority_recount.stderr"
cmp -s "$SINGLE_AUTHORITY" "$SINGLE_AUTHORITY_RECOUNT" || \
  abort 26 "independent Goal5848 authority recount is not byte-identical"

stage "capture_post_transaction_machine_state"
nvidia-smi -q -i 0 > "$OUTPUT_ROOT/environment/gpu_state_after.txt"
nvidia-smi --query-compute-apps=pid,process_name,used_memory \
  --format=csv,noheader,nounits \
  > "$OUTPUT_ROOT/environment/gpu_compute_processes_after.txt" || true
if [[ -s "$OUTPUT_ROOT/environment/gpu_compute_processes_after.txt" ]]; then
  abort 24 "Goal5848 left active compute processes on visible GPU 0"
fi
printf '%s\n' "$EXPECTED_COMMIT" > "$OUTPUT_ROOT/environment/source_commit.txt"
printf '%s\n' "$PREDECESSOR_COMMIT" > "$OUTPUT_ROOT/environment/predecessor_commit.txt"

stage "archive_source_revisions"
git -C "$PYOPTIX_SOURCE" archive --format=tar.gz \
  -o "$OUTPUT_ROOT/pyoptix-source.tar.gz" HEAD
git -C "$OPTIX_HEADERS" archive --format=tar.gz \
  -o "$OUTPUT_ROOT/optix-headers-source.tar.gz" HEAD

stage "build_evidence_manifest"
"$PYTHON" - "$OUTPUT_ROOT" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve(strict=True)
included = (
    "logs", "environment", "pyoptix-build", "current-native",
    "predecessor-native", "direct", "device-artifacts", "signing-roots",
    "current-aot", "current-aot-cache", "predecessor-candidates", "aot-hit",
    "timer-free-witness", "baseline-competence", "instrumentation-overhead",
    "formal-transaction", "preregistration.json", "preflight.json",
    "single-generation-authority.json",
    "single-generation-authority.recount.json", "pyoptix-source.tar.gz",
    "optix-headers-source.tar.gz",
)
rows = []
for relative in included:
    start = root / relative
    paths = [start] if start.is_file() else sorted(start.rglob("*"))
    for path in paths:
        if path.is_symlink():
            raise RuntimeError(f"evidence contains symlink: {path}")
        if not path.is_file():
            continue
        payload = path.read_bytes()
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
body = {
    "schema": "rtdl.goal5848.evidence_manifest.v1",
    "status": "PASS__ONE_GENERATION_COMPLETE_EVIDENCE_FILE_SET",
    "rows": rows,
    "file_count": len(rows),
    "payload_bytes": sum(row["bytes"] for row in rows),
    "retry_count": 0,
    "discard_count": 0,
    "external_review_complete": False,
    "public_or_manuscript_claim_authorized": False,
}
encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("ascii")
body["manifest_sha256"] = hashlib.sha256(encoded).hexdigest()
(root / "EVIDENCE_MANIFEST.json").write_text(
    json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="ascii"
)
PY

stage "package_return_evidence"
ARCHIVE="${OUTPUT_ROOT}.tar.gz"
test ! -e "$ARCHIVE"
ARCHIVE_MEMBERS=(
  logs environment pyoptix-build current-native predecessor-native direct
  device-artifacts signing-roots current-aot current-aot-cache
  predecessor-candidates aot-hit timer-free-witness baseline-competence
  instrumentation-overhead formal-transaction preregistration.json
  preflight.json single-generation-authority.json
  single-generation-authority.recount.json pyoptix-source.tar.gz
  optix-headers-source.tar.gz EVIDENCE_MANIFEST.json
)
tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
  -cf - -C "$OUTPUT_ROOT" "${ARCHIVE_MEMBERS[@]}" | gzip -n > "$ARCHIVE"
sha256sum "$ARCHIVE" > "${ARCHIVE}.sha256"

stage "remove_unarchived_predecessor_worktree"
if [[ "$PREDECESSOR_WORKTREE_CREATED" -eq 1 ]]; then
  git -C "$REPO_ROOT" worktree remove --force "$PREDECESSOR_ROOT"
  PREDECESSOR_WORKTREE_CREATED=0
fi
test -z "$(git -C "$REPO_ROOT" status --porcelain=v1 --untracked-files=all)"

trap - ERR
printf 'GOAL5848_SINGLE_GENERATION_COMPLETE\narchive=%s\nsha256_file=%s\nauthority=%s\n' \
  "$ARCHIVE" "${ARCHIVE}.sha256" "$SINGLE_AUTHORITY"
