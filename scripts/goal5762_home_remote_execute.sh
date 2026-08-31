#!/usr/bin/env bash
set -euo pipefail

ROOT=${1:?usage: goal5762_home_remote_execute.sh SOURCE_ROOT OUTPUT_ROOT}
OUTPUT=${2:?usage: goal5762_home_remote_execute.sh SOURCE_ROOT OUTPUT_ROOT}
OPTIX_PREFIX=${OPTIX_PREFIX:-/home/lestat/vendor/optix-dev}
CUDA_PREFIX=${CUDA_PREFIX:-/usr/lib/cuda}
NVCC=${NVCC:-/usr/bin/nvcc}

test ! -e "$OUTPUT"
test -x /usr/bin/g++-12
test -f "$OPTIX_PREFIX/include/optix.h"
test -x "$NVCC"
test -f /usr/lib/x86_64-linux-gnu/libnvvm.so
test -f "$CUDA_PREFIX/nvvm/libdevice/libdevice.10.bc"

cd "$ROOT"
rm -f build/librtdl_optix.so
make build-optix \
  OPTIX_PREFIX="$OPTIX_PREFIX" \
  CUDA_PREFIX="$CUDA_PREFIX" \
  OPTIX_CUDA_ARCH=sm_61 \
  CXX_OPTIX="$NVCC -ccbin /usr/bin/g++-12"

export PYTHONPATH="$ROOT/src:$ROOT"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
export NUMBA_CUDA_NVVM=/usr/lib/x86_64-linux-gnu/libnvvm.so
export NUMBA_CUDA_LIBDEVICE="$CUDA_PREFIX/nvvm/libdevice/libdevice.10.bc"
python3 scripts/goal5762_home_exact_predicate_witness_validation.py \
  --native "$ROOT/build/librtdl_optix.so" \
  --optix-include "$OPTIX_PREFIX/include" \
  --cuda-include "$CUDA_PREFIX/include" \
  --output "$OUTPUT"
python3 scripts/goal5762_recount_home_exact_predicate_witness.py \
  --raw "$OUTPUT" \
  --output "${OUTPUT}_RECOUNT.json"
