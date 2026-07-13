#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
WORK_DIR="${APP_DIR}/_work/author_official"
BIN="${AUTHOR_BINARY:-${WORK_DIR}/OWLRayTracing/build-rtdl-rtbarneshut/rtbarneshut}"
INPUT_FILE="${1:-${APP_DIR}/_runs/author_smoke/rtbarneshut_author_new_input.txt}"
RUN_DIR="${APP_DIR}/_runs/author_same_input"
LOG="${RUN_DIR}/author_treelogy.log"
FORCE_OUT="${RUN_DIR}/author_treelogy_forces.txt"
PREPARED_OUT="${RUN_DIR}/author_treelogy_prepared_arrays.json"

mkdir -p "${RUN_DIR}"

if [ ! -x "${BIN}" ]; then
  echo "Author binary not found or not executable: ${BIN}" >&2
  echo "Run scripts/setup_author_official.sh first." >&2
  exit 2
fi

if [ ! -f "${INPUT_FILE}" ]; then
  echo "Input file not found: ${INPUT_FILE}" >&2
  echo "Run scripts/run_author_smoke.sh first or pass an explicit input file." >&2
  exit 2
fi

RTBH_FORCE_OUT="${FORCE_OUT}" RTBH_PREPARED_ARRAYS_OUT="${PREPARED_OUT}" "${BIN}" treelogy "${INPUT_FILE}" | tee "${LOG}"

python3 - "$LOG" "${FORCE_OUT}" "${PREPARED_OUT}" "${RUN_DIR}/summary.json" <<'PY'
from pathlib import Path
import json
import re
import sys

log_path = Path(sys.argv[1])
force_path = Path(sys.argv[2])
prepared_path = Path(sys.argv[3])
summary_path = Path(sys.argv[4])
text = log_path.read_text(errors="replace")

def find_ms(label: str) -> float | None:
    pattern = rf"{re.escape(label)}\s*:?\s*([0-9.]+)"
    match = re.search(pattern, text)
    if not match:
        return None
    value = float(match.group(1))
    return value * 1000.0 if value < 1.0 else value

summary = {
    "mode": "author_treelogy_same_input",
    "log": str(log_path),
    "force_output": str(force_path),
    "force_output_exists": force_path.exists(),
    "force_line_count": sum(1 for _ in force_path.open()) if force_path.exists() else 0,
    "prepared_arrays_output": str(prepared_path),
    "prepared_arrays_output_exists": prepared_path.exists(),
    "preprocessing_ms": find_ms("Preprocessing Time"),
    "rt_core_force_ms": find_ms("RT Cores Force Calculations time"),
    "execution_ms": find_ms("Execution time"),
    "paper_reproduction_complete": False,
    "same_input_comparator_attempted": True
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(summary_path)
PY
