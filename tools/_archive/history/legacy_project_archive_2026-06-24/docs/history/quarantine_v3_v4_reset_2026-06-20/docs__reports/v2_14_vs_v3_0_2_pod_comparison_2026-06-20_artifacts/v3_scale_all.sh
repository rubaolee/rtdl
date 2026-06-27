#!/usr/bin/env bash
set -euo pipefail
source "${ART}/bench_env.sh"
cd "${REPO}"
activate_repo_venv
python scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --materialize-rayjoin-public-cdb \
  --timeout-scale 2.5 \
  --heartbeat-sec 30 \
  --stdout-tail 12000 \
  --stderr-tail 12000 \
  --output-dir "${ART}/v3.0.2_current_scale_outputs" \
  --output-json "${ART}/v3.0.2_current_scale_summary.json"
