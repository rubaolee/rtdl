#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
APP_DIR="${ROOT_DIR}/Paper-reproduction-apps/rt-barneshut-paper"
RUN_DIR="${APP_DIR}/_runs/author_contract_reference"
INPUT_FILE="${INPUT_FILE:-}"
SYNTHETIC_COUNT="${SYNTHETIC_COUNT:-64}"

mkdir -p "${RUN_DIR}"

ARGS=(
  --force-output "${RUN_DIR}/author_contract_reference_forces.txt"
  --summary "${RUN_DIR}/summary.json"
)

if [ -n "${INPUT_FILE}" ]; then
  ARGS+=(--input "${INPUT_FILE}")
else
  ARGS+=(--synthetic-count "${SYNTHETIC_COUNT}" --write-synthetic-input "${RUN_DIR}/synthetic_input.txt")
fi

cd "${ROOT_DIR}"
PYTHON="${PYTHON:-python3}"
PYTHONPATH=src:. "${PYTHON}" Paper-reproduction-apps/rt-barneshut-paper/author_contract_reference.py "${ARGS[@]}"
