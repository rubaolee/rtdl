#!/usr/bin/env bash
set -euo pipefail
source "${ART}/bench_env.sh"
cd "${REPO}"
activate_repo_venv
python scripts/run_test_matrix.py --group v3_current
