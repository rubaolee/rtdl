#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
RUN_DIR="${APP_DIR}/_runs/generic_aggregate_force_same_input_gate"

PYTHON="${PYTHON:-python3}"
AUTHOR_FORCE="${AUTHOR_FORCE:-${APP_DIR}/_runs/author_same_input/author_treelogy_forces.txt}"
PREPARED_ARRAYS="${PREPARED_ARRAYS:-${APP_DIR}/_runs/author_same_input/author_treelogy_prepared_arrays.json}"

mkdir -p "${RUN_DIR}"
PYTHONPATH="${ROOT_DIR}/src:${ROOT_DIR}:${PYTHONPATH:-}" "${PYTHON}" \
  "${APP_DIR}/scripts/run_generic_aggregate_force_same_input_gate.py" \
  --prepared-arrays "${PREPARED_ARRAYS}" \
  --expected-force "${AUTHOR_FORCE}" \
  --run-dir "${RUN_DIR}" \
  --rtol "${RTBH_GENERIC_FORCE_COMPARE_RTOL:-1e-4}" \
  --atol "${RTBH_GENERIC_FORCE_COMPARE_ATOL:-1e-4}"
