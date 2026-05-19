#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_DIR="${ARTIFACT_DIR:-docs/reports/goal2392_rt_dbscan_pod}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-240}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENDOR_ROOT="${VENDOR_ROOT:-${HOME}/vendor}"
OPTIX_SDK_TAG="${OPTIX_SDK_TAG:-v8.0.0}"
OPTIX_PREFIX="${OPTIX_PREFIX:-${VENDOR_ROOT}/optix-sdk}"
INSTALL_CUPY_IF_MISSING="${INSTALL_CUPY_IF_MISSING:-1}"
INSTALL_OPTIX_SDK_IF_MISSING="${INSTALL_OPTIX_SDK_IF_MISSING:-1}"
APP="examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"

mkdir -p "${ARTIFACT_DIR}"

log() {
  printf '[goal2392][%s] %s\n' "$(date -u +%H:%M:%S)" "$*"
}

run_json() {
  local name="$1"
  shift
  log "start ${name}"
  timeout "${STEP_TIMEOUT_SECONDS}" "$@" > "${ARTIFACT_DIR}/${name}.json"
  log "done ${name}: ${ARTIFACT_DIR}/${name}.json"
}

probe_cupy() {
  "${PYTHON_BIN}" - <<'PY'
import cupy
print(cupy.__version__, cupy.cuda.runtime.getDeviceCount())
PY
}

ensure_cupy() {
  if probe_cupy; then
    return 0
  fi
  if [ "${INSTALL_CUPY_IF_MISSING}" != "1" ]; then
    return 1
  fi
  log "CuPy missing; installing cupy-cuda12x"
  "${PYTHON_BIN}" -m pip install -q cupy-cuda12x || "${PYTHON_BIN}" -m pip install --break-system-packages -q cupy-cuda12x
  probe_cupy
}

ensure_optix_sdk() {
  if [ -d "${OPTIX_PREFIX}/include" ]; then
    return 0
  fi
  if [ "${INSTALL_OPTIX_SDK_IF_MISSING}" != "1" ]; then
    return 1
  fi
  log "OptiX SDK headers missing; cloning ${OPTIX_SDK_TAG} into ${OPTIX_PREFIX}"
  mkdir -p "$(dirname "${OPTIX_PREFIX}")"
  git clone --depth 1 --branch "${OPTIX_SDK_TAG}" https://github.com/NVIDIA/optix-sdk "${OPTIX_PREFIX}"
}

log "record environment"
{
  printf 'commit=%s\n' "$(git rev-parse HEAD)"
  printf 'python=%s\n' "$("${PYTHON_BIN}" --version 2>&1)"
  command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi --query-gpu=name,driver_version --format=csv,noheader || true
  command -v nvcc >/dev/null 2>&1 && nvcc --version | tail -n 1 || true
  printf 'RTDL_OPTIX_LIBRARY=%s\n' "${RTDL_OPTIX_LIBRARY:-}"
} > "${ARTIFACT_DIR}/environment.txt"

export PYTHONPATH="src:."

log "cpu correctness smoke"
run_json tiny_cpu_reference "${PYTHON_BIN}" "${APP}" --mode cpu_reference --dataset tiny --include-rows
run_json tiny_rtdl_cpu_rows "${PYTHON_BIN}" "${APP}" --mode rtdl_cpu_rows --dataset tiny --include-rows

log "probe CuPy partner"
if ensure_cupy; then
  run_json clustered3d_partner_spatial_bucket_4096 "${PYTHON_BIN}" "${APP}" --mode partner_spatial_bucket_3d --dataset clustered3d --point-count 4096 --partner cupy --no-validation
  run_json road3d_partner_spatial_bucket_4096 "${PYTHON_BIN}" "${APP}" --mode partner_spatial_bucket_3d --dataset road3d --point-count 4096 --partner cupy --no-validation
  run_json clustered3d_partner_cupy_grid_4096 "${PYTHON_BIN}" "${APP}" --mode partner_cupy_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
  run_json road3d_partner_cupy_grid_4096 "${PYTHON_BIN}" "${APP}" --mode partner_cupy_grid_components_3d --dataset road3d --point-count 4096 --no-validation
  run_json ngsim_dense_partner_cupy_grid_4096 "${PYTHON_BIN}" "${APP}" --mode partner_cupy_grid_components_3d --dataset ngsim_dense --point-count 4096 --no-validation
else
  log "skip CuPy partner rows: CuPy unavailable"
fi

log "probe/build OptiX"
if [ -z "${RTDL_OPTIX_LIBRARY:-}" ]; then
  if ensure_optix_sdk; then
    log "building OptiX with OPTIX_PREFIX=${OPTIX_PREFIX}"
    make build-optix OPTIX_PREFIX="${OPTIX_PREFIX}"
    export RTDL_OPTIX_LIBRARY="${PWD}/build/librtdl_optix.so"
  else
    log "skip OptiX rows: RTDL_OPTIX_LIBRARY unset and OPTIX_PREFIX missing"
  fi
fi

if [ -n "${RTDL_OPTIX_LIBRARY:-}" ] && [ -f "${RTDL_OPTIX_LIBRARY}" ]; then
  run_json clustered3d_optix_prepared_rows_1024 "${PYTHON_BIN}" "${APP}" --mode optix_prepared_rows --dataset clustered3d --point-count 1024 --no-validation
  run_json road3d_optix_prepared_rows_1024 "${PYTHON_BIN}" "${APP}" --mode optix_prepared_rows --dataset road3d --point-count 1024 --no-validation
  if ensure_cupy; then
    run_json clustered3d_optix_core_flags_cupy_grid_4096 "${PYTHON_BIN}" "${APP}" --mode optix_core_flags_cupy_grid_components_3d --dataset clustered3d --point-count 4096 --no-validation
    run_json road3d_optix_core_flags_cupy_grid_4096 "${PYTHON_BIN}" "${APP}" --mode optix_core_flags_cupy_grid_components_3d --dataset road3d --point-count 4096 --no-validation
  else
    log "skip OptiX+CuPy bridge rows: CuPy unavailable"
  fi
else
  log "skip OptiX rows: library unavailable"
fi

log "goal2392 pod runner complete"
