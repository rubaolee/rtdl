#!/usr/bin/env bash
set -euo pipefail
cd /workspace/rtdl_goal4817_user_smoke_20260630_102224
mkdir -p /workspace/goal4842_midpoint_full
RTDL_OPTIX_LIB=/workspace/rtdl_goal4817_user_smoke_20260630_102224/build/librtdl_optix.so \
PYTHONPATH=src \
python3 history/internal_docs/goal4842_midpoint_scaled_pip_probe.py \
  --base /workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb \
  --sx -33924059549367 \
  --sy 9057003035588 \
  --output-json /workspace/goal4842_midpoint_full/rtdl_midpoint_full.json \
  > /workspace/goal4842_midpoint_full/run.log \
  2>&1
