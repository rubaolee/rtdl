#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
RUN_DIR="${APP_DIR}/_runs/author_contract_rtdl_cuda_gate"
INPUT_FILE="${INPUT_FILE:-}"
SYNTHETIC_COUNT="${SYNTHETIC_COUNT:-64}"
REPEATS="${REPEATS:-5}"
PYTHON="${PYTHON:-python3}"

mkdir -p "${RUN_DIR}"

AUTHOR_ARGS=(
  --force-output "${RUN_DIR}/author_contract_forces.txt"
  --write-rtdl-prepared-arrays "${RUN_DIR}/author_prepared_arrays_for_rtdl.json"
  --summary "${RUN_DIR}/author_contract_summary.json"
)

if [ -n "${INPUT_FILE}" ]; then
  AUTHOR_ARGS+=(--input "${INPUT_FILE}")
else
  AUTHOR_ARGS+=(--synthetic-count "${SYNTHETIC_COUNT}" --write-synthetic-input "${RUN_DIR}/synthetic_input.txt")
fi

cd "${ROOT_DIR}"

echo "[1/3] Build author-contract force reference and generic prepared arrays"
PYTHONPATH=src:. "${PYTHON}" Paper-reproduction-apps/rt-barneshut-paper/author_contract_reference.py "${AUTHOR_ARGS[@]}"

echo "[2/3] Run RTDL CUDA diagnostic over author-prepared aggregate arrays"
PYTHONPATH=src:. "${PYTHON}" Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py \
  --mode rtdl-3d-diagnostic \
  --body-count "${SYNTHETIC_COUNT}" \
  --repeats "${REPEATS}" \
  --prepared-arrays-json "${RUN_DIR}/author_prepared_arrays_for_rtdl.json" \
  --traversal-policy author-opening \
  --output "${RUN_DIR}/rtdl_summary.json" \
  --force-output "${RUN_DIR}/rtdl_forces.txt" \
  --force-output-scale 0.1

echo "[3/3] Compare author-contract reference forces to RTDL CUDA forces"
PYTHONPATH=src:. "${PYTHON}" Paper-reproduction-apps/rt-barneshut-paper/scripts/compare_force_outputs.py \
  --left "${RUN_DIR}/author_contract_forces.txt" \
  --right "${RUN_DIR}/rtdl_forces.txt" \
  --rtol "${RTBH_CONTRACT_RTDL_FORCE_RTOL:-1e-4}" \
  --atol "${RTBH_CONTRACT_RTDL_FORCE_ATOL:-1e-4}" \
  --output "${RUN_DIR}/author_contract_vs_rtdl_cuda_compare.json"

"${PYTHON}" - "${RUN_DIR}/summary.json" "${RUN_DIR}/author_contract_summary.json" "${RUN_DIR}/rtdl_summary.json" "${RUN_DIR}/author_contract_vs_rtdl_cuda_compare.json" <<'PY'
from pathlib import Path
import json
import sys

summary_path = Path(sys.argv[1])
author_path = Path(sys.argv[2])
rtdl_path = Path(sys.argv[3])
compare_path = Path(sys.argv[4])
author = json.loads(author_path.read_text())
rtdl = json.loads(rtdl_path.read_text())
compare = json.loads(compare_path.read_text())
summary = {
    "mode": "author_contract_vs_rtdl_cuda_prepared_arrays_gate",
    "author_contract_summary": str(author_path),
    "rtdl_summary": str(rtdl_path),
    "compare": str(compare_path),
    "matched": bool(compare["matched"]),
    "force_count": compare["common_count"],
    "max_abs_error": compare["max_abs_error"],
    "max_rel_error": compare["max_rel_error"],
    "mismatch_count": compare["mismatch_count"],
    "rtdl_same_tree_contract_as_authors": bool(rtdl.get("same_tree_contract_as_authors")),
    "rtdl_traversal_policy": rtdl.get("traversal_policy"),
    "prepared_arrays_contract_source": author.get("rtdl_prepared_arrays"),
    "paper_reproduction_complete": False,
    "claim_boundary": (
        "POD diagnostic gate only: compares the Python author-contract reference "
        "against the RTDL CUDA diagnostic consuming author-prepared aggregate arrays. "
        "The patched author binary remains the paper comparator."
    ),
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(summary_path)
PY
