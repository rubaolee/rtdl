#!/usr/bin/env bash
set -euo pipefail
cd /root/rtdl_v3_rebuild_20260620/current
source /root/rtdl_v3_rebuild_20260620/.venv/bin/activate
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
echo "START $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "GPU $(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | head -n 1)"
python scripts/v3_0_m62_barnes_hut_current_route_rerank.py \
  --body-counts 32768,65536,131072 \
  --repeat 17 \
  --warmup 3 \
  --output /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_rerank_32768_65536_131072_r17.json
echo "END $(date -u +%Y-%m-%dT%H:%M:%SZ)"
