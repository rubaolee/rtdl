#!/usr/bin/env bash
set -euo pipefail

RESULT_DIR="${RESULT_DIR:-docs/reports/goal1450_v1_5_2_prepared_host_output_pod_results_2026-05-07}"
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

echo "Goal1450 v1.5.2 prepared host-output pod executor"
echo "result_dir=${RESULT_DIR}"
echo "optix_prefix=${OPTIX_PREFIX:-auto}"
echo "cuda_prefix=${CUDA_PREFIX}"
echo "nvcc=${NVCC}"

{
  echo "Goal1450 pod environment"
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
} | tee "${RESULT_DIR}/goal1450_pod_environment.log"

if [ -n "${OPTIX_PREFIX}" ]; then
  build_command=(make build-optix "OPTIX_PREFIX=${OPTIX_PREFIX}" "CUDA_PREFIX=${CUDA_PREFIX}" "NVCC=${NVCC}")
else
  build_command=(make build-optix "CUDA_PREFIX=${CUDA_PREFIX}" "NVCC=${NVCC}")
fi

set +e
"${build_command[@]}" 2>&1 | tee "${RESULT_DIR}/goal1450_make_build_optix.log"
build_rc=${PIPESTATUS[0]}
set -e

python3 - "${build_rc}" "${RESULT_DIR}/goal1450_make_build_optix.log" \
  "${RESULT_DIR}/goal1450_make_build_optix.status.json" <<'PY'
from __future__ import annotations

import json
import sys

payload = {
    "label": "goal1450_make_build_optix",
    "exit_code": int(sys.argv[1]),
    "log": sys.argv[2],
    "status": "ok" if int(sys.argv[1]) == 0 else "failed",
    "claim_boundary": "Build status only; does not authorize true zero-copy, public speedup, stable primitive, or release claim.",
}
open(sys.argv[3], "w", encoding="utf-8").write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY

if [ "${build_rc}" -ne 0 ]; then
  echo "Goal1450 build-optix failed; see ${RESULT_DIR}/goal1450_make_build_optix.log" >&2
  exit "${build_rc}"
fi

export PYTHONPATH="${PYTHONPATH:-src:.}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"

set +e
python3 scripts/goal1450_v1_5_2_prepared_host_output_parity.py \
  --backends embree optix \
  --required-backends embree optix \
  --json-out "${RESULT_DIR}/goal1450_prepared_host_output_parity_pod_required_2026-05-07.json" \
  --md-out "${RESULT_DIR}/goal1450_prepared_host_output_parity_pod_required_2026-05-07.md" \
  2>&1 | tee "${RESULT_DIR}/goal1450_prepared_host_output_parity_pod_required.log"
parity_rc=${PIPESTATUS[0]}
set -e

python3 - "${parity_rc}" "${RESULT_DIR}/goal1450_prepared_host_output_parity_pod_required.log" \
  "${RESULT_DIR}/goal1450_prepared_host_output_parity_pod_required.status.json" <<'PY'
from __future__ import annotations

import json
import sys

payload = {
    "label": "goal1450_prepared_host_output_parity_pod_required",
    "exit_code": int(sys.argv[1]),
    "log": sys.argv[2],
    "status": "ok" if int(sys.argv[1]) == 0 else "failed",
    "claim_boundary": "Required Embree+OptiX parity status only; does not authorize true zero-copy, public speedup, stable primitive, or release claim.",
}
open(sys.argv[3], "w", encoding="utf-8").write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY

python3 - "${RESULT_DIR}" <<'PY' | tee "${RESULT_DIR}/goal1450_pod_summary.json"
from __future__ import annotations

import json
import sys
from pathlib import Path

result_dir = Path(sys.argv[1])
statuses = [
    json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(result_dir.glob("*.status.json"))
]
parity_path = result_dir / "goal1450_prepared_host_output_parity_pod_required_2026-05-07.json"
parity = json.loads(parity_path.read_text(encoding="utf-8")) if parity_path.exists() else {}
payload = {
    "goal": "Goal1450",
    "scope": "v1.5.2 prepared host-output required Embree+OptiX parity",
    "status_count": len(statuses),
    "failed_count": sum(1 for row in statuses if row["exit_code"] != 0),
    "failed_labels": [row["label"] for row in statuses if row["exit_code"] != 0],
    "parity_accepted": parity.get("accepted"),
    "backend_summary": parity.get("backend_summary"),
    "required_backends": parity.get("required_backends"),
    "skipped_required": parity.get("skipped_required"),
    "claim_boundary": (
        "Pod summary records required-backend parity evidence only. It does not "
        "authorize true zero-copy, public speedup wording, whole-app claims, "
        "stable primitive wording, or release action."
    ),
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

echo "Goal1450 pod executor complete"
echo "result_dir=${RESULT_DIR}"
exit "${parity_rc}"
