#!/usr/bin/env bash
set -euo pipefail
ROOT=${1:?usage: script SOURCE_ROOT OUTPUT_ROOT}
OUTPUT=${2:?usage: script SOURCE_ROOT OUTPUT_ROOT}
test ! -e "$OUTPUT"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
export NUMBA_CUDA_NVVM=/usr/lib/x86_64-linux-gnu/libnvvm.so
export NUMBA_CUDA_LIBDEVICE=/usr/lib/cuda/nvvm/libdevice/libdevice.10.bc
export RTDL_OPTIX_LIB="$ROOT/build/librtdl_optix.so"
export RTDL_OPTIX_LIBRARY="$ROOT/build/librtdl_optix.so"
python3 scripts/goal5773_home_triangle_reduction_lifecycle_validation.py \
  --native "$ROOT/build/librtdl_optix.so" \
  --optix-include /home/lestat/vendor/optix-dev/include \
  --cuda-include /usr/lib/cuda/include \
  --output "$OUTPUT"
sha256sum "$ROOT/build/librtdl_optix.so" "$OUTPUT/RESULT.json"
