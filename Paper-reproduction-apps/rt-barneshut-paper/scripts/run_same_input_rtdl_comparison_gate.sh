#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
GATE_DIR="${APP_DIR}/_runs/same_input_rtdl_comparison_gate"
AUTHOR_FORCE="${AUTHOR_FORCE:-${APP_DIR}/_runs/author_same_input/author_treelogy_forces.txt}"
INPUT_FILE="${INPUT_FILE:-${APP_DIR}/_runs/author_smoke/rtbarneshut_author_new_input.txt}"
SORTED_INPUT="${GATE_DIR}/author_sorted_input_for_rtdl.txt"
PREPARED_ARRAYS="${GATE_DIR}/author_prepared_arrays_for_rtdl.json"
AUTHOR_BINARY_PREPARED_ARRAYS="${AUTHOR_BINARY_PREPARED_ARRAYS:-${APP_DIR}/_runs/author_same_input/author_treelogy_prepared_arrays.json}"

mkdir -p "${GATE_DIR}"

if [ ! -f "${AUTHOR_FORCE}" ]; then
  echo "Author force output not found: ${AUTHOR_FORCE}" >&2
  echo "Run scripts/run_author_comparator_gate.sh first." >&2
  exit 2
fi

if [ ! -f "${INPUT_FILE}" ]; then
  echo "Same-input body file not found: ${INPUT_FILE}" >&2
  echo "Run scripts/run_author_comparator_gate.sh first." >&2
  exit 2
fi

echo "[1/3] Select same-input prepared aggregate arrays for RTDL"
if [ -f "${AUTHOR_BINARY_PREPARED_ARRAYS}" ]; then
  SELECTED_TRAVERSAL_POLICY="${TRAVERSAL_POLICY:-author-optix-payload}"
  cp "${AUTHOR_BINARY_PREPARED_ARRAYS}" "${PREPARED_ARRAYS}"
  python3 - "${AUTHOR_BINARY_PREPARED_ARRAYS}" "${PREPARED_ARRAYS}" "${GATE_DIR}/author_sorted_input_summary.json" "${SELECTED_TRAVERSAL_POLICY}" <<'PY'
from pathlib import Path
import json
import sys

source = Path(sys.argv[1])
selected = Path(sys.argv[2])
summary = Path(sys.argv[3])
selected_traversal_policy = sys.argv[4]
payload = json.loads(source.read_text())
summary.write_text(json.dumps({
    "mode": "author_binary_prepared_arrays_selected",
    "source": str(source),
    "selected": str(selected),
    "schema": payload.get("schema"),
    "contract_source": payload.get("contract_source"),
    "point_count": len(payload.get("points", [])),
    "node_count": len(payload.get("nodes", [])),
    "ordered_primary_launch_ray_count": len(payload.get("ordered_primary_launch_rays", [])),
    "selected_traversal_policy": selected_traversal_policy,
    "claim_boundary": "Uses the patched author binary's dumped prepared state; no Python tree reconstruction."
}, indent=2, sort_keys=True) + "\n")
print(summary)
PY
else
  SELECTED_TRAVERSAL_POLICY="${TRAVERSAL_POLICY:-author-opening}"
  echo "Author binary prepared arrays not found: ${AUTHOR_BINARY_PREPARED_ARRAYS}" >&2
  echo "Falling back to Python reconstructed author tree; this remains a diagnostic fallback, not paper closure." >&2
  python3 "${APP_DIR}/author_contract_reference.py" \
    --input "${INPUT_FILE}" \
    --write-author-sorted-input "${SORTED_INPUT}" \
    --write-rtdl-prepared-arrays "${PREPARED_ARRAYS}" \
    --summary "${GATE_DIR}/author_sorted_input_summary.json"
  python3 - "${GATE_DIR}/author_sorted_input_summary.json" "${SELECTED_TRAVERSAL_POLICY}" <<'PY'
from pathlib import Path
import json
import sys

path = Path(sys.argv[1])
payload = json.loads(path.read_text())
payload["selected_traversal_policy"] = sys.argv[2]
path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
PY
fi

echo "[2/3] Run RTDL 3-D diagnostic on author-prepared aggregate arrays"
BODY_COUNT="${BODY_COUNT:-32768}" \
REPEATS="${REPEATS:-5}" \
INPUT_FILE="${SORTED_INPUT}" \
PREPARED_ARRAYS_JSON="${PREPARED_ARRAYS}" \
TRAVERSAL_POLICY="${SELECTED_TRAVERSAL_POLICY}" \
bash "${APP_DIR}/scripts/run_rtdl_diagnostic.sh"

RTDL_FORCE="${APP_DIR}/_runs/rtdl_diagnostic/rtdl_forces.txt"
COMPARE_OUT="${GATE_DIR}/author_vs_rtdl_force_compare.json"

echo "[3/3] Compare author force output to RTDL force output"
set +e
python3 "${APP_DIR}/scripts/compare_force_outputs.py" \
  --left "${AUTHOR_FORCE}" \
  --right "${RTDL_FORCE}" \
  --rtol "${RTBH_AUTHOR_RTDL_FORCE_RTOL:-1e-4}" \
  --atol "${RTBH_AUTHOR_RTDL_FORCE_ATOL:-1e-4}" \
  --output "${COMPARE_OUT}"
COMPARE_STATUS=$?
set -e

python3 - "${GATE_DIR}/summary.json" "${COMPARE_OUT}" "${GATE_DIR}/author_sorted_input_summary.json" <<'PY'
from pathlib import Path
import json
import sys

summary_path = Path(sys.argv[1])
compare_path = Path(sys.argv[2])
prepared_summary_path = Path(sys.argv[3])
compare = json.loads(compare_path.read_text())
prepared_summary = json.loads(prepared_summary_path.read_text())
summary = {
    "mode": "same_input_author_vs_rtdl_force_gate",
    "author_vs_rtdl_compare": str(compare_path),
    "prepared_arrays_summary": str(prepared_summary_path),
    "prepared_contract_source": prepared_summary.get("contract_source"),
    "prepared_source_mode": prepared_summary.get("mode"),
    "rtdl_contract": "author_binary_or_bucket_tree_over_generic_flat_aggregate_arrays",
    "traversal_policy": prepared_summary.get("selected_traversal_policy"),
    "matched": bool(compare["matched"]),
    "force_count": compare["common_count"],
    "max_abs_error": compare["max_abs_error"],
    "max_rel_error": compare["max_rel_error"],
    "mismatch_count": compare["mismatch_count"],
    "same_input_author_rtdl_comparator_closed": bool(compare["matched"]),
    "paper_reproduction_complete": False,
    "claim_boundary": "A match would compare force files, but paper reproduction still requires matched contract and phase-boundary review."
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(summary_path)
PY

if [ "${COMPARE_STATUS}" -ne 0 ]; then
  exit "${COMPARE_STATUS}"
fi
