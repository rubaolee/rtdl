#!/usr/bin/env bash
set -euo pipefail

ROOT=${1:?usage: goal5773_home_hierarchy_execute.sh SOURCE_ROOT OUTPUT_ROOT}
OUTPUT=${2:?usage: goal5773_home_hierarchy_execute.sh SOURCE_ROOT OUTPUT_ROOT}
test ! -e "$OUTPUT"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT"
export RTDL_OPTIX_LIB="$ROOT/build/librtdl_optix.so"
export RTDL_OPTIX_LIBRARY="$ROOT/build/librtdl_optix.so"

python3 -m unittest \
  tests.goal5764_v4_hierarchy_frontier_test \
  tests.goal5773_v4_prepared_application_lifecycle_test \
  tests.goal5773_v4_prepared_hierarchy_lifecycle_test
python3 scripts/goal5773_home_hierarchy_lifecycle_validation.py \
  --native "$ROOT/build/librtdl_optix.so" \
  --output "$OUTPUT"
sha256sum "$ROOT/build/librtdl_optix.so" "$OUTPUT/RESULT.json"
