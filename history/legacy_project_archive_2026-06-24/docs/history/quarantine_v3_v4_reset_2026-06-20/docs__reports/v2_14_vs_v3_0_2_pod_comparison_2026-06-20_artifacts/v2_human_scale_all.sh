#!/usr/bin/env bash
set -euo pipefail
source "${ART}/bench_env.sh"
cd "${REPO}"
activate_repo_venv
python scripts/rtdl_human_scale_rt_vs_embree_comparison.py --output-dir "${ART}/v2.14_human_scale_same_contract"
