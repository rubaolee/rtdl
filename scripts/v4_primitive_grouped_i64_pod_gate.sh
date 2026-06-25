#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

detect_optix_prefix() {
  if [[ -n "${OPTIX_PREFIX:-}" && -f "${OPTIX_PREFIX}/include/optix.h" ]]; then
    printf '%s\n' "$OPTIX_PREFIX"
    return 0
  fi
  for candidate in \
    /root/vendor/optix-sdk \
    /root/vendor/optix-dev \
    /workspace/vendor/optix-dev-9.0.0 \
    /workspace/vendor/optix-dev-8.0.0 \
    /workspace/vendor/optix-dev \
    "${HOME:-/root}/vendor/optix-sdk" \
    "${HOME:-/root}/vendor/optix-dev" \
    /opt/optix \
    /usr/local/optix; do
    if [[ -f "${candidate}/include/optix.h" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

PYTHON_BIN="${PYTHON_BIN:-python3}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr}"
OPTIX_PREFIX="$(detect_optix_prefix)"
RAY_COUNTS="${RAY_COUNTS:-32768,131072}"
GROUP_WIDTH="${GROUP_WIDTH:-16}"
REPEAT="${REPEAT:-7}"
WARMUP="${WARMUP:-2}"
OUT_JSON="${OUT_JSON:-future/v4/evidence/v4_primitive_grouped_i64_device_outputs_pod_gate_$(date -u +%Y%m%d_%H%M%S).json}"

echo "[v4-grouped-i64] root=$ROOT"
echo "[v4-grouped-i64] python=$PYTHON_BIN"
echo "[v4-grouped-i64] optix=$OPTIX_PREFIX"
echo "[v4-grouped-i64] cuda=$CUDA_PREFIX"
echo "[v4-grouped-i64] ray_counts=$RAY_COUNTS group_width=$GROUP_WIDTH repeat=$REPEAT warmup=$WARMUP"

nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader || true

make build-optix OPTIX_PREFIX="$OPTIX_PREFIX" CUDA_PREFIX="$CUDA_PREFIX"
export RTDL_OPTIX_LIBRARY="$ROOT/build/librtdl_optix.so"
export PYTHONPATH="src:."

"$PYTHON_BIN" scripts/v4_primitive_grouped_i64_device_outputs_validation.py \
  --ray-counts "$RAY_COUNTS" \
  --group-width "$GROUP_WIDTH" \
  --repeat "$REPEAT" \
  --warmup "$WARMUP" \
  --progress \
  --json-out "$OUT_JSON"

echo "[v4-grouped-i64] wrote $OUT_JSON"
