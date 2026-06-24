#!/usr/bin/env bash
set -euo pipefail
cd /root/rtdl_v3_rebuild_20260620/current
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY="$PWD/build/librtdl_optix.so"
ART=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_grouped_reduction_device_columns_20260621
{
  echo "START $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
  ../.venv/bin/python --version
  for rows_groups in "262144 1024" "524288 2048"; do
    set -- $rows_groups
    rows=$1
    groups=$2
    echo "RUN device_columns rows=$rows groups=$groups $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ../.venv/bin/python scripts/v3_0_m28_raydb_prepared_grouped_refresh.py \
      --generated-rows "$rows" --generated-groups "$groups" --generated-revenue-mod 64 \
      --modes sum --backends embree,optix --warmup 3 \
      --repeat-overrides embree:sum=100,optix:sum=100 \
      --optix-ray-batch-layout cupy_device_columns \
      --output "$ART/grouped_sum_device_columns_${rows}_repeat100.json"
    echo "RUN host_packed_optix rows=$rows groups=$groups $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ../.venv/bin/python scripts/v3_0_m28_raydb_prepared_grouped_refresh.py \
      --generated-rows "$rows" --generated-groups "$groups" --generated-revenue-mod 64 \
      --modes sum --backends optix --warmup 3 \
      --repeat-overrides optix:sum=100 \
      --optix-ray-batch-layout host_packed \
      --output "$ART/grouped_sum_host_packed_optix_${rows}_repeat100.json"
  done
  echo "DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} 2>&1 | tee "$ART/run_device_columns_repeat100.log"
