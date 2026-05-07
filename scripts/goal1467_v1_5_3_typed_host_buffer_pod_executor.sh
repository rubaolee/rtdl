#!/usr/bin/env bash
set -euo pipefail

RESULT_DIR="${RESULT_DIR:-docs/reports/goal1467_v1_5_3_typed_host_buffer_pod_results_2026-05-07}"
OPTIX_PREFIX="${OPTIX_PREFIX:-}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
if [ -z "${NVCC:-}" ]; then
  if [ -x "${CUDA_PREFIX}/bin/nvcc" ]; then
    NVCC="${CUDA_PREFIX}/bin/nvcc"
  else
    NVCC="$(command -v nvcc || true)"
  fi
fi
if [ -z "${NVCC}" ]; then
  NVCC="${CUDA_PREFIX}/bin/nvcc"
fi

mkdir -p "${RESULT_DIR}"

echo "Goal1467 v1.5.3 typed host buffer pod executor"
echo "result_dir=${RESULT_DIR}"
echo "optix_prefix=${OPTIX_PREFIX:-auto}"
echo "cuda_prefix=${CUDA_PREFIX}"
echo "nvcc=${NVCC}"

{
  echo "Goal1467 pod environment"
  date -u
  uname -a
  git rev-parse HEAD || true
  git status --short || true
  nvidia-smi || true
  python3 --version || true
  command -v nvcc || true
  nvcc --version || true
  echo "OPTIX_PREFIX=${OPTIX_PREFIX:-auto}"
  echo "CUDA_PREFIX=${CUDA_PREFIX}"
  echo "NVCC=${NVCC}"
} | tee "${RESULT_DIR}/goal1467_pod_environment.log"

if [ -n "${OPTIX_PREFIX}" ]; then
  build_command=(make build-optix "OPTIX_PREFIX=${OPTIX_PREFIX}" "CUDA_PREFIX=${CUDA_PREFIX}" "NVCC=${NVCC}")
else
  build_command=(make build-optix "CUDA_PREFIX=${CUDA_PREFIX}" "NVCC=${NVCC}")
fi

set +e
"${build_command[@]}" 2>&1 | tee "${RESULT_DIR}/goal1467_make_build_optix.log"
build_rc=${PIPESTATUS[0]}
set -e

if [ "${build_rc}" -ne 0 ]; then
  echo "Goal1467 build-optix failed; see ${RESULT_DIR}/goal1467_make_build_optix.log" >&2
  exit "${build_rc}"
fi

export PYTHONPATH="${PYTHONPATH:-src:.}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"

set +e
python3 scripts/goal1467_v1_5_3_typed_host_buffer_parity.py \
  --backends embree optix \
  --required-backends embree optix \
  --json-out "${RESULT_DIR}/goal1467_typed_host_buffer_parity_required_2026-05-07.json" \
  --md-out "${RESULT_DIR}/goal1467_typed_host_buffer_parity_required_2026-05-07.md" \
  2>&1 | tee "${RESULT_DIR}/goal1467_typed_host_buffer_parity_required.log"
parity_rc=${PIPESTATUS[0]}
set -e

python3 - "${RESULT_DIR}" "${parity_rc}" <<'PY' | tee "${RESULT_DIR}/goal1467_pod_summary.json"
from __future__ import annotations

import json
import sys
from pathlib import Path

result_dir = Path(sys.argv[1])
parity_rc = int(sys.argv[2])
parity_path = result_dir / "goal1467_typed_host_buffer_parity_required_2026-05-07.json"
parity = json.loads(parity_path.read_text(encoding="utf-8")) if parity_path.exists() else {}
payload = {
    "goal": "Goal1467",
    "scope": "v1.5.3 typed host input plus prepared host output required Embree+OptiX parity",
    "exit_code": parity_rc,
    "parity_accepted": parity.get("accepted"),
    "backend_summary": parity.get("backend_summary"),
    "required_backends": parity.get("required_backends"),
    "skipped_required": parity.get("skipped_required"),
    "claim_boundary": (
        "Pod summary records required-backend parity evidence only. It does "
        "not authorize true zero-copy, public speedup wording, whole-app "
        "claims, stable primitive promotion, partner tensor handoff, or "
        "release action."
    ),
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

echo "Goal1467 pod executor complete"
echo "result_dir=${RESULT_DIR}"
exit "${parity_rc}"
