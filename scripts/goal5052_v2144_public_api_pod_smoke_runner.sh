#!/usr/bin/env bash
set -euo pipefail

# Goal5052 runner for an already-running RTX-class Linux POD.
# Boundary: runtime smoke only; no public speedup or true-zero-copy claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export RTDL_OPTIX_LIBRARY="${RTDL_OPTIX_LIBRARY:-$(pwd)/build/librtdl_optix.so}"

OUTPUT_JSON="${1:-history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json}"

echo "Goal5052 v2.14.4 public API POD smoke"
echo "git_head=$(git rev-parse HEAD 2>/dev/null || true)"
echo "RTDL_OPTIX_LIBRARY=${RTDL_OPTIX_LIBRARY}"
date -u +"utc_start=%Y-%m-%dT%H:%M:%SZ"
nvidia-smi || true

python3 scripts/goal5052_v2144_public_api_pod_smoke.py \
  --strict \
  --output-json "${OUTPUT_JSON}"

date -u +"utc_end=%Y-%m-%dT%H:%M:%SZ"
echo "Goal5052 complete: ${OUTPUT_JSON}"
