#!/usr/bin/env bash
set -euo pipefail
cd /root/rtdl_v3_rebuild_20260620/current
source /root/rtdl_v3_rebuild_20260620/.venv/bin/activate
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
export CUDA_PYTHON_DISABLE_MAJOR_VERSION_WARNING=1
ART=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m6_barnes_hut_20260620
PART=$ART/partitioned
echo "START_PARTITIONED $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "GPU $(nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | head -n 1)"
for bodies in 32768 65536 131072; do
  echo "BODY_START $bodies $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  python scripts/v3_0_m62_barnes_hut_current_route_rerank.py \
    --body-counts "$bodies" \
    --repeat 11 \
    --warmup 3 \
    --output "$PART/m6_barnes_hut_${bodies}_r11.json"
  echo "BODY_END $bodies $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader | head -n 1 || true
done
python - <<'PY'
import json
from pathlib import Path
ART=Path('/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m6_barnes_hut_20260620')
parts=[json.loads((ART/'partitioned'/f'm6_barnes_hut_{b}_r11.json').read_text()) for b in (32768,65536,131072)]
merged={k:v for k,v in parts[0].items() if k not in {'body_counts','rows','comparisons','raw_payloads'}}
merged['body_counts']=[b for part in parts for b in part['body_counts']]
merged['rows']=[row for part in parts for row in part['rows']]
merged['comparisons']=[row for part in parts for row in part['comparisons']]
merged['raw_payloads']=[row for part in parts for row in part.get('raw_payloads', [])]
merged['partitioning']='one_body_count_per_process_to_avoid_runner_raw_payload_memory_retention'
merged['source_parts']=[str(ART/'partitioned'/f'm6_barnes_hut_{b}_r11.json') for b in (32768,65536,131072)]
(ART/'m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json').write_text(json.dumps(merged, indent=2, sort_keys=True)+'\n')
print(json.dumps({'merged_rows': len(merged['rows']), 'body_counts': merged['body_counts']}, sort_keys=True))
PY
echo "END_PARTITIONED $(date -u +%Y-%m-%dT%H:%M:%SZ)"
