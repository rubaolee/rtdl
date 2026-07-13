#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
RUN_DIR="${APP_DIR}/_runs/rtdl_diagnostic"
BODY_COUNT="${BODY_COUNT:-32768}"
REPEATS="${REPEATS:-5}"
INPUT_FILE="${INPUT_FILE:-}"
PREPARED_ARRAYS_JSON="${PREPARED_ARRAYS_JSON:-}"
TRAVERSAL_POLICY="${TRAVERSAL_POLICY:-rtdl-containment}"

mkdir -p "${RUN_DIR}"

ARGS=(
  --mode rtdl-3d-diagnostic
  --body-count "${BODY_COUNT}"
  --repeats "${REPEATS}"
  --output "${RUN_DIR}/summary.json"
  --force-output "${RUN_DIR}/rtdl_forces.txt"
  --force-output-scale "${FORCE_OUTPUT_SCALE:-0.1}"
  --traversal-policy "${TRAVERSAL_POLICY}"
)

if [ -n "${INPUT_FILE}" ]; then
  ARGS+=(--input-file "${INPUT_FILE}")
fi

if [ -n "${PREPARED_ARRAYS_JSON}" ]; then
  ARGS+=(--prepared-arrays-json "${PREPARED_ARRAYS_JSON}")
fi

cd "${ROOT_DIR}"
PYTHONPATH=src:. python Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py "${ARGS[@]}"
