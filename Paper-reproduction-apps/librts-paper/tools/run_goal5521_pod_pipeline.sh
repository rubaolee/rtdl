#!/usr/bin/env bash
set -euo pipefail

while [[ ! -s /tmp/goal5521-stage/precheck.json ]]; do
  if ! kill -0 "${GOAL5521_PRECHECK_PID:?}" 2>/dev/null; then
    echo "precheck process exited without a result" >&2
    cat /tmp/goal5521-stage/precheck.log >&2 || true
    exit 1
  fi
  sleep 5
done

python - <<'PY'
import json
from pathlib import Path

result = json.loads(Path("/tmp/goal5521-stage/precheck.json").read_text())
if not result["decision"]["authorize_rtdl_cache_and_matrix"]:
    raise SystemExit(3)
PY

cd /tmp/rtdl-goal5519/Paper-reproduction-apps/librts-paper
export PYTHONPATH=/tmp/rtdl-goal5519/src:/tmp/rtdl-goal5519/Paper-reproduction-apps/librts-paper

python /tmp/goal5521-stage/build_cache.py \
  --geometry /tmp/goal5521-target/PPoPPAE/datasets/polygons/parks.bz2.wkt \
  --cache-prefix /tmp/goal5521-stage/parks_bz2_mbr \
  --output /tmp/goal5521-stage/cache_build.json

RTDL_OPTIX_LIB=/tmp/rtdl-goal5519/build5519/librtdl_optix.so \
python /tmp/goal5521-stage/run_matrix.py \
  --base-target /tmp/goal5521-target \
  --pairs /tmp/goal5521-stage/pairs.json \
  --extraction /tmp/goal5521-stage/extraction.json \
  --cache-prefix /tmp/goal5521-stage/parks_bz2_mbr \
  --precheck /tmp/goal5521-stage/precheck.json \
  --shared-serialize-dir /tmp/goal5521-stage/serialize/shared \
  --output /tmp/goal5521-stage/gate.json
