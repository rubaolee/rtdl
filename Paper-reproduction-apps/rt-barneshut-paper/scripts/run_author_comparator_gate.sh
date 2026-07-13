#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
GATE_DIR="${APP_DIR}/_runs/author_comparator_gate"
mkdir -p "${GATE_DIR}"

echo "[1/4] Build patched AuthorOfficial"
bash "${APP_DIR}/scripts/setup_author_official.sh"

echo "[2/4] Run author new mode with force dump"
bash "${APP_DIR}/scripts/run_author_smoke.sh"

INPUT_FILE="${APP_DIR}/_runs/author_smoke/rtbarneshut_author_new_input.txt"
NEW_FORCE="${APP_DIR}/_runs/author_smoke/author_new_forces.txt"

echo "[3/4] Run author treelogy same-input mode with force dump"
bash "${APP_DIR}/scripts/run_author_same_input.sh" "${INPUT_FILE}"

TRE_FORCE="${APP_DIR}/_runs/author_same_input/author_treelogy_forces.txt"
COMPARE_OUT="${GATE_DIR}/author_new_vs_treelogy_force_compare.json"

echo "[4/4] Compare author new vs treelogy per-body force outputs"
python3 "${APP_DIR}/scripts/compare_force_outputs.py" \
  --left "${NEW_FORCE}" \
  --right "${TRE_FORCE}" \
  --rtol "${RTBH_FORCE_RTOL:-1e-5}" \
  --atol "${RTBH_FORCE_ATOL:-1e-5}" \
  --output "${COMPARE_OUT}"

python3 - "${GATE_DIR}/summary.json" "${COMPARE_OUT}" <<'PY'
from pathlib import Path
import json
import sys

summary_path = Path(sys.argv[1])
compare_path = Path(sys.argv[2])
compare = json.loads(compare_path.read_text())
summary = {
    "mode": "author_comparator_gate",
    "author_new_vs_treelogy_compare": str(compare_path),
    "matched": bool(compare["matched"]),
    "force_count": compare["left_count"],
    "max_abs_error": compare["max_abs_error"],
    "max_rel_error": compare["max_rel_error"],
    "same_input_author_comparator_closed": bool(compare["matched"]),
    "paper_reproduction_complete": False
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(summary_path)
PY
