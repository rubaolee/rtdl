#!/usr/bin/env bash
set -euo pipefail
BASE=/root/rtdl_v3_rebuild_20260620
RUN_DIR=$(cd "$(dirname "$0")" && pwd)
echo "[fixed-radius-cache] run_dir=$RUN_DIR"
echo "[fixed-radius-cache] start=$(date -u --iso-8601=seconds)"
echo "[fixed-radius-cache] nvidia=$(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | head -n 1 || true)"
run_goal2626() {
  local tree=$1
  local app=$2
  cd "$BASE/$tree"
  echo "[fixed-radius-cache] $tree goal2626 large $app"
  PYTHONPATH=src python3 scripts/goal2626_benchmark_embree_optix_baseline.py \
    --scale large \
    --artifact-dir "$RUN_DIR/${tree}_goal2626_large_${app}" \
    --case-repeat 5 \
    --only-app "$app" \
    --timeout-sec 2400
}
run_goal2636() {
  local tree=$1
  local app=$2
  cd "$BASE/$tree"
  echo "[fixed-radius-cache] $tree goal2636 stress $app"
  PYTHONPATH=src python3 scripts/goal2636_strengthen_benchmark_rows.py \
    --tier stress \
    --artifact-dir "$RUN_DIR/${tree}_goal2636_stress_${app}" \
    --case-repeat 5 \
    --only-app "$app" \
    --timeout-sec 2400
}
for tree in v2_14 current; do
  for app in hausdorff_xhd rt_dbscan barnes_hut; do
    run_goal2626 "$tree" "$app"
  done
  for app in hausdorff_xhd barnes_hut; do
    run_goal2636 "$tree" "$app"
  done
done
echo "[fixed-radius-cache] artifact hashes"
find "$RUN_DIR" -name summary.json -print0 | sort -z | xargs -0 sha256sum
echo "[fixed-radius-cache] end=$(date -u --iso-8601=seconds)"
