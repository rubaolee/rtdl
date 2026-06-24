#!/usr/bin/env bash
set -euo pipefail
BASE=/root/rtdl_v3_rebuild_20260620
RUN_DIR="$1"
echo "[rtnn-cache] run_dir=$RUN_DIR"
echo "[rtnn-cache] start=$(date -Is)"
echo "[rtnn-cache] nvidia=$(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | head -n 1 || true)"
cd "$BASE/v2_14"
echo "[rtnn-cache] running v2_14 goal2636 rtnn stress repeat5"
PYTHONPATH=src:. python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier stress \
  --artifact-dir "$RUN_DIR/v2_14_goal2636_rtnn_stress" \
  --case-repeat 5 \
  --only-app rtnn \
  --timeout-sec 2400
cd "$BASE/current"
echo "[rtnn-cache] running current patched goal2636 rtnn stress repeat5"
PYTHONPATH=src:. python3 scripts/goal2636_strengthen_benchmark_rows.py \
  --tier stress \
  --artifact-dir "$RUN_DIR/current_patched_goal2636_rtnn_stress" \
  --case-repeat 5 \
  --only-app rtnn \
  --timeout-sec 2400
echo "[rtnn-cache] artifact hashes"
sha256sum \
  "$RUN_DIR/v2_14_goal2636_rtnn_stress/summary.json" \
  "$RUN_DIR/current_patched_goal2636_rtnn_stress/summary.json"
echo "[rtnn-cache] end=$(date -Is)"
