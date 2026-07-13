#!/usr/bin/env bash
set -u -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PYTHON="${PYTHON:-python3}"

cd "${ROOT_DIR}"

PYTHONPATH=src:. "${PYTHON}" \
  Paper-reproduction-apps/rt-barneshut-paper/scripts/run_completion_audit.py
