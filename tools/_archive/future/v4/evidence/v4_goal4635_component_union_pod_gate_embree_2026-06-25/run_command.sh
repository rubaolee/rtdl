#!/usr/bin/env bash
set -euo pipefail
cd /root/rtdl_v4_candidate_pod
PYTHONPATH=src:. python3 scripts/v3_phoenix_component_union_m38_pod_ab.py \
  --output-dir future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25 \
  --dataset clustered3d --point-count 262144 --radius 3.0 --min-neighbors 4 \
  --seed 20260625 --warmup 1 --repeat 5 --heartbeat-sec 30 --hard-cap-sec 7200 \
  --require-rt-hardware
