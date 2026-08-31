#!/usr/bin/env bash
set -euo pipefail

# One create-only Home exercise of every exact V4 application path.  The V2
# halves are retained because each smoke is also the final-byte equality and
# behavioral-OptiX gate.  The shared cache is writable only during this target
# preparation transaction and becomes read-only after the manifest is sealed.

SOURCE_ROOT=${SOURCE_ROOT:?}
OUTPUT_ROOT=${OUTPUT_ROOT:?}
PYTHON=${PYTHON:?}
NATIVE=${NATIVE:?}
OPTIX_INCLUDE=${OPTIX_INCLUDE:?}
CUDA_INCLUDE=${CUDA_INCLUDE:?}

if [[ -e "${OUTPUT_ROOT}" ]]; then
  echo "refusing to replace Goal5776 leaf-cache population root" >&2
  exit 2
fi
mkdir "${OUTPUT_ROOT}"
mkdir "${OUTPUT_ROOT}/cache"

export PYTHONPATH="${SOURCE_ROOT}/src:${SOURCE_ROOT}/scripts:${SOURCE_ROOT}"
export RTDL_OPTIX_LIB="${NATIVE}"
export RTDL_OPTIX_LIBRARY="${NATIVE}"
export RTDL_V4_FORMAL_LEAF_CACHE="${OUTPUT_ROOT}/cache"
unset RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST
unset RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256

run() {
  local label=$1
  shift
  printf 'START %s\n' "${label}"
  "${PYTHON}" "$@"
  printf 'PASS %s\n' "${label}"
}

DATA=/home/lestat/data/rtdl_goal5634_replay_21156f9c

run particle "${SOURCE_ROOT}/scripts/goal5776_home_particle_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" \
  --input-root /home/lestat/data/goal5776_particle_prepared_v2 \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}" --output "${OUTPUT_ROOT}/particle.json"

run triangle_com_dblp \
  "${SOURCE_ROOT}/scripts/goal5776_home_triangle_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" \
  --edge-file /home/lestat/data/goal5776_snap/edges/com-dblp.edge \
  --dataset com-dblp --expected-triangle-count 2224385 \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}" --output "${OUTPUT_ROOT}/triangle.json"

run rtdbscan "${SOURCE_ROOT}/scripts/goal5776_home_rtdbscan_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" \
  --input-root /home/lestat/work/goal5776_rtdbscan_prepared_v1 \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}" --output "${OUTPUT_ROOT}/rtdbscan.json"

run rtnn "${SOURCE_ROOT}/scripts/goal5776_home_rtnn_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" \
  --input-root /home/lestat/data/goal5776_rtnn_prepared_v1 \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}" --output "${OUTPUT_ROOT}/rtnn.json"

run xhd "${SOURCE_ROOT}/scripts/goal5776_home_xhd_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" \
  --input-root /home/lestat/data/goal5776_xhd_prepared_v1 \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}" --output "${OUTPUT_ROOT}/xhd.json"

run rt_barneshut \
  "${SOURCE_ROOT}/scripts/goal5776_home_rt_barneshut_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" \
  --prepared-arrays "${DATA}/rt_barneshut/prepared_arrays.json" \
  --expected-forces "${DATA}/rt_barneshut/expected_forces.txt" \
  --expected-prepared-sha256 78908bba758f2a222b4c771d838083f94ff9ea709d004ae21061409f5eeb55d9 \
  --expected-forces-sha256 6add3a3cc10037e66ec81ab08e2f9c32f4fb24c56db6950cf9946f43d5a87b28 \
  --native "${NATIVE}" --output "${OUTPUT_ROOT}/rt_barneshut.json"

run raydb "${SOURCE_ROOT}/scripts/goal5776_home_raydb_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" --packet "${DATA}/raydb/q11/packet.json" \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}" --output "${OUTPUT_ROOT}/raydb.json"

run librts "${SOURCE_ROOT}/scripts/goal5776_home_librts_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" \
  --cache-npz "${DATA}/librts/parks/cache/parks_bz2.npz" \
  --cache-json "${DATA}/librts/parks/cache/parks_bz2.json" \
  --point-queries "${DATA}/librts/parks/queries/point_contains_100000.wkt" \
  --range-queries "${DATA}/librts/parks/queries/range_contains_100000.wkt" \
  --native "${NATIVE}" --output "${OUTPUT_ROOT}/librts.json"

run rayjoin "${SOURCE_ROOT}/scripts/goal5776_home_rayjoin_real_scale_smoke.py" \
  --source-root "${SOURCE_ROOT}" \
  --left "${DATA}/rayjoin/top4_county.cdb" \
  --right "${DATA}/rayjoin/top4_zipcode.cdb" \
  --native "${NATIVE}" --optix-include "${OPTIX_INCLUDE}" \
  --cuda-include "${CUDA_INCLUDE}" --output "${OUTPUT_ROOT}/rayjoin.json"

"${PYTHON}" - "${OUTPUT_ROOT}/cache" "${OUTPUT_ROOT}/MANIFEST.json" <<'PY'
from pathlib import Path
import sys
from rtdsl.v4_callback_numba_codegen import materialize_formal_numba_leaf_cache_manifest

materialize_formal_numba_leaf_cache_manifest(Path(sys.argv[1]), Path(sys.argv[2]))
PY

chmod -R a-w "${OUTPUT_ROOT}/cache"
printf 'SEALED %s\n' "${OUTPUT_ROOT}/MANIFEST.json"
