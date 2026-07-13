#!/usr/bin/env bash
set -euo pipefail
cd /workspace/rtdl_goal4817_user_smoke_20260630_102224
mkdir -p /workspace/goal4841_after_double_contract_60000
RTDL_OPTIX_LIB=/workspace/rtdl_goal4817_user_smoke_20260630_102224/build/librtdl_optix.so \
PYTHONPATH=src \
python3 history/internal_docs/goal4840_chain_prefix_probe_scaled_points.py \
  --left /workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb \
  --right /workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb \
  --output-json /workspace/goal4841_after_double_contract_60000/prefix_60000.json \
  --max-chains 60000 \
  > /workspace/goal4841_after_double_contract_60000/prefix_run.log \
  2>&1
