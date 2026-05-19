#!/usr/bin/env bash
set -euo pipefail

RTDL_ROOT="${RTDL_ROOT:-$(pwd)}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
CUDA_PREFIX="${CUDA_PREFIX:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
OUT_DIR="${OUT_DIR:-$RTDL_ROOT/docs/reports/goal2368_rtnn_prepared_column_pod}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-900}"
RADIUS="${RADIUS:-0.02}"
K_MAX="${K_MAX:-50}"
REPEAT="${REPEAT:-3}"

log() {
  printf '[goal2368] %s\n' "$*" >&2
}

run_step() {
  local name="$1"
  shift
  log "START $name"
  timeout "${STEP_TIMEOUT_SECONDS}s" "$@"
  log "DONE  $name"
}

cd "$RTDL_ROOT"
mkdir -p "$OUT_DIR"

log "root=$RTDL_ROOT"
log "out_dir=$OUT_DIR"
log "head=$(git rev-parse --short HEAD 2>/dev/null || printf unknown)"
log "gpu=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -1 || printf unavailable)"
log "cuda_paths=$(ls -d /usr/local/cuda* 2>/dev/null | tr '\n' ' ' || true)"
log "optix_prefix=$OPTIX_PREFIX"

if [[ -n "$CUDA_PREFIX" ]]; then
  run_step build-optix make build-optix "OPTIX_PREFIX=$OPTIX_PREFIX" "CUDA_PREFIX=$CUDA_PREFIX"
else
  run_step build-optix make build-optix "OPTIX_PREFIX=$OPTIX_PREFIX"
fi

export PYTHONPATH="$RTDL_ROOT/src:$RTDL_ROOT"
export RTDL_OPTIX_LIBRARY="$RTDL_ROOT/build/librtdl_optix.so"

for count in 65536 262144; do
  point_file="$OUT_DIR/uniform3d_${count}.csv"
  run_step "generate-${count}" "$PYTHON_BIN" scripts/goal2348_rtnn_v2_2_external_runner.py \
    generate \
    --point-file "$point_file" \
    --point-count "$count" \
    --dimension 3 \
    --json-out "$OUT_DIR/generate_${count}.json"

  run_step "records-run-optix-${count}" "$PYTHON_BIN" scripts/goal2348_rtnn_v2_2_external_runner.py \
    run-rtdl-current-3d-neighbors-smoke \
    --point-file "$point_file" \
    --radius "$RADIUS" \
    --k-max "$K_MAX" \
    --result-mode raw \
    --input-mode records \
    --execution-mode run-optix \
    --repeat "$REPEAT" \
    --row-label "records_run_optix_${count}" \
    --json-out "$OUT_DIR/rtdl_records_run_optix_3d_${count}_r002_k50.json"

  run_step "packed-run-optix-${count}" "$PYTHON_BIN" scripts/goal2348_rtnn_v2_2_external_runner.py \
    run-rtdl-current-3d-neighbors-smoke \
    --point-file "$point_file" \
    --radius "$RADIUS" \
    --k-max "$K_MAX" \
    --result-mode raw \
    --input-mode packed-columns \
    --execution-mode run-optix \
    --repeat "$REPEAT" \
    --row-label "packed_run_optix_${count}" \
    --json-out "$OUT_DIR/rtdl_packed_run_optix_3d_${count}_r002_k50.json"

  run_step "packed-prepared-optix-${count}" "$PYTHON_BIN" scripts/goal2348_rtnn_v2_2_external_runner.py \
    run-rtdl-current-3d-neighbors-smoke \
    --point-file "$point_file" \
    --radius "$RADIUS" \
    --k-max "$K_MAX" \
    --result-mode raw \
    --input-mode packed-columns \
    --execution-mode prepared-optix \
    --repeat "$REPEAT" \
    --row-label "packed_prepared_optix_${count}" \
    --json-out "$OUT_DIR/rtdl_packed_prepared_optix_3d_${count}_r002_k50.json"
done

log "artifacts:"
find "$OUT_DIR" -maxdepth 1 -type f -name '*.json' -printf '  %p\n' | sort >&2
