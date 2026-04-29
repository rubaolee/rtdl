#!/usr/bin/env bash
set -euo pipefail

# Goal1085 generated runner for a local/Linux/Windows non-cloud Embree baseline host.
# Boundary: does not authorize public RTX speedup claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export RTDL_GOAL1085_START_CHUNK="${RTDL_GOAL1085_START_CHUNK:-0}"
export RTDL_GOAL1085_END_CHUNK="${RTDL_GOAL1085_END_CHUNK:-179}"
export RTDL_GOAL1085_SKIP_EXISTING="${RTDL_GOAL1085_SKIP_EXISTING:-1}"

if [ "${RTDL_GOAL1085_START_CHUNK}" -lt 0 ] || [ "${RTDL_GOAL1085_END_CHUNK}" -gt 179 ] || [ "${RTDL_GOAL1085_START_CHUNK}" -gt "${RTDL_GOAL1085_END_CHUNK}" ]; then
  echo "invalid chunk range ${RTDL_GOAL1085_START_CHUNK}..${RTDL_GOAL1085_END_CHUNK}" >&2
  exit 2
fi

mkdir -p docs/reports/goal1085_robot_chunked_embree_baseline
for chunk_index in $(seq "${RTDL_GOAL1085_START_CHUNK}" "${RTDL_GOAL1085_END_CHUNK}"); do
  output_json="docs/reports/goal1085_robot_chunked_embree_baseline/chunk_${chunk_index}.json"
  if [ "${RTDL_GOAL1085_SKIP_EXISTING}" = "1" ] && [ -s "${output_json}" ]; then
    echo "Skipping existing robot Embree baseline chunk ${chunk_index}"
    continue
  fi
  echo "Running robot Embree baseline chunk ${chunk_index}"
  PYTHONPATH=src:. python3 scripts/goal839_robot_pose_count_baseline.py --backend embree --pose-count 200000 --obstacle-count 4096 --iterations 3 --worker-count 8 --pose-id-start $(( chunk_index * 200000 + 1 )) --output-json docs/reports/goal1085_robot_chunked_embree_baseline/chunk_${chunk_index}.json
done
echo "Goal1085 complete. Review docs/reports/goal1085_robot_chunked_embree_baseline/chunk_*.json before any comparison."
