#!/usr/bin/env bash
set -euo pipefail

ROOT=/tmp/goal5760_home
CUDA_ROOT="${ROOT}/toolchain/usr/local/cuda-12.8"
SOURCE_ROOT="${ROOT}/source"

test -d "${ROOT}"
test -f "${ROOT}/goal5760_source.tar.gz"
test -f "${ROOT}/goal5760_optix.tar.gz"
test -f "${ROOT}/librtdl_optix.so"
rm -rf "${ROOT}/toolchain" "${ROOT}/source" "${ROOT}/optix" "${ROOT}/result"
mkdir "${ROOT}/toolchain" "${ROOT}/source" "${ROOT}/optix"
find "${ROOT}/debs" -name '*.deb' -exec dpkg-deb -x {} "${ROOT}/toolchain" \;
tar -xzf "${ROOT}/goal5760_source.tar.gz" -C "${SOURCE_ROOT}"
tar -xzf "${ROOT}/goal5760_optix.tar.gz" -C "${ROOT}/optix"

export PATH="${CUDA_ROOT}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export PYTHONPATH="${SOURCE_ROOT}/src:${SOURCE_ROOT}"
export LD_LIBRARY_PATH="${CUDA_ROOT}/nvvm/lib64:${CUDA_ROOT}/targets/x86_64-linux/lib:/usr/lib/x86_64-linux-gnu"
export NUMBA_CUDA_NVVM="${CUDA_ROOT}/nvvm/lib64/libnvvm.so"
export NUMBA_CUDA_LIBDEVICE="${CUDA_ROOT}/nvvm/libdevice/libdevice.10.bc"
export RTDL_OPTIX_LIB="${ROOT}/librtdl_optix.so"

python3 "${SOURCE_ROOT}/scripts/goal5760_home_bounded_relation_device_validation.py" \
  --native "${ROOT}/librtdl_optix.so" \
  --optix-include "${ROOT}/optix/include" \
  --cuda-include "${CUDA_ROOT}/include" \
  --output "${ROOT}/result"
