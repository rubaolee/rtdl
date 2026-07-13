#!/usr/bin/env bash
set -euo pipefail

while [[ ! -s /tmp/goal5523-stage/extraction.json ]]; do
  if ! kill -0 "${GOAL5523_EXTRACTION_PID:?}" 2>/dev/null; then
    echo "Goal5523 extraction exited without evidence" >&2
    cat /tmp/goal5523-stage/extraction.log >&2 || true
    exit 1
  fi
  sleep 5
done

cd /tmp/rtdl-goal5519/Paper-reproduction-apps/librts-paper
export PYTHONPATH=/tmp/rtdl-goal5519/src:/tmp/rtdl-goal5519/Paper-reproduction-apps/librts-paper

python /tmp/goal5523-stage/build_cache.py \
  --geometry /tmp/goal5523-target/PPoPPAE/datasets/polygons/parks_Europe.wkt \
  --cache-prefix /tmp/goal5523-stage/parks_europe_mbr \
  --output /tmp/goal5523-stage/cache_build.json

mkdir -p /tmp/goal5523-stage/serialize/shared
RTDL_OPTIX_LIB=/tmp/rtdl-goal5519/build5519/librtdl_optix.so \
python /tmp/goal5523-stage/run_matrix.py \
  --base-target /tmp/goal5523-target \
  --pairs /tmp/goal5523-stage/pairs.json \
  --extraction /tmp/goal5523-stage/extraction.json \
  --cache-prefix /tmp/goal5523-stage/parks_europe_mbr \
  --shared-serialize-dir /tmp/goal5523-stage/serialize/shared \
  --output /tmp/goal5523-stage/gate.json \
  --geometry-member PPoPPAE/datasets/polygons/parks_Europe.wkt \
  --case-prefix parks_Europe \
  --schema-name rtdl.paper_reproduction.librts.goal5523_parks_europe_point_cardinality_gate.v1 \
  --checkpoint-schema rtdl.paper_reproduction.librts.goal5523_point_cardinality_checkpoint.v1 \
  --matched-status parks_europe_exact_point_contains_five_cardinality_matrix_matched \
  --mismatch-status parks_europe_exact_point_contains_cardinality_matrix_has_mismatch
