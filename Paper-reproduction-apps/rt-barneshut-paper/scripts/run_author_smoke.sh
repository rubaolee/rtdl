#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
WORK_DIR="${APP_DIR}/_work/author_official"
BIN="${AUTHOR_BINARY:-${WORK_DIR}/OWLRayTracing/build-rtdl-rtbarneshut/rtbarneshut}"
RUN_DIR="${APP_DIR}/_runs/author_smoke"
OUT_INPUT="${RUN_DIR}/rtbarneshut_author_new_input.txt"
LOG="${RUN_DIR}/author_new.log"
FORCE_OUT="${RUN_DIR}/author_new_forces.txt"

mkdir -p "${RUN_DIR}"

if [ ! -x "${BIN}" ]; then
  echo "Author binary not found or not executable: ${BIN}" >&2
  echo "Run scripts/setup_author_official.sh first." >&2
  exit 2
fi

RTBH_FORCE_OUT="${FORCE_OUT}" "${BIN}" new "${OUT_INPUT}" | tee "${LOG}"

python3 - "$LOG" "${RUN_DIR}/summary.json" <<'PY'
from pathlib import Path
import json
import re
import sys

log_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
text = log_path.read_text(errors="replace")

def find_ms(label: str) -> float | None:
    pattern = rf"{re.escape(label)}\s*:?\s*([0-9.]+)"
    match = re.search(pattern, text)
    if not match:
        return None
    value = float(match.group(1))
    return value * 1000.0 if value < 1.0 else value

summary = {
    "mode": "author_new_smoke",
    "log": str(log_path),
    "input": str(log_path.parent / "rtbarneshut_author_new_input.txt"),
    "force_output": str(log_path.parent / "author_new_forces.txt"),
    "force_output_exists": (log_path.parent / "author_new_forces.txt").exists(),
    "preprocessing_ms": find_ms("Preprocessing Time"),
    "rt_core_force_ms": find_ms("RT Cores Force Calculations time"),
    "execution_ms": find_ms("Execution time"),
    "paper_reproduction_complete": False,
    "same_input_comparator_closed": False
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(summary_path)
PY
