#!/usr/bin/env bash
set -euo pipefail

# Goal1085 generated runner for a local/Linux/Windows non-cloud Embree baseline host.
# Boundary: does not authorize public RTX speedup claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
mkdir -p docs/reports/goal1085_robot_chunked_embree_baseline
for chunk_index in $(seq 0 179); do
  echo "Running robot Embree baseline chunk ${chunk_index}"
  PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py --backend embree --pose-count 200000 --obstacle-count 4096 --iterations 3 --worker-count 8 --output-json docs/reports/goal1085_robot_chunked_embree_baseline/chunk_${chunk_index}.json
done
echo "Goal1085 complete. Review docs/reports/goal1085_robot_chunked_embree_baseline/chunk_*.json before any comparison."
