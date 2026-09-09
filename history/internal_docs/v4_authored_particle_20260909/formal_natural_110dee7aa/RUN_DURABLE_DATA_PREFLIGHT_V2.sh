#!/usr/bin/env bash
set -euo pipefail

DURABLE_ROOT=${DURABLE_ROOT:-/workspace/rtdl-particle-110dee7aa-durable}
SOURCE_ROOT=${SOURCE_ROOT:-/tmp/rtdl-particle-110dee7aa}
PYTHON=${PYTHON:-/tmp/rtdl-crossgpu/venv/bin/python}

export PYTHONPATH="$SOURCE_ROOT/src:$SOURCE_ROOT"

"$PYTHON" "$DURABLE_ROOT/successor_v2/postformal_particle_reconstruct_durable_v2.py" \
  --source-root "$SOURCE_ROOT" \
  --archive "$DURABLE_ROOT/artifacts/formal/rtdl-authored-particle-formal-110dee7aa.tar.gz" \
  --base-particle-dir "$DURABLE_ROOT/data/base_particle" \
  --ensemble-dir "$DURABLE_ROOT/data/transition_ensemble" \
  --data-preflight-only
