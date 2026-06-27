#!/usr/bin/env bash
set -euo pipefail
source "${ART}/bench_env.sh"
cd "${REPO}"
activate_repo_venv
make build-embree
