#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: build_direct_measurement.sh OPTIX_INCLUDE CUDA_INCLUDE OUTPUT" >&2
  exit 2
fi

optix_include="$1"
cuda_include="$2"
output="$3"

test ! -e "$output"
g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  -isystem "$optix_include" -I"$cuda_include" \
  "$(dirname "$0")/direct_measurement.cpp" \
  -L"$(dirname "$cuda_include")/lib64" -lcuda -lnvrtc -ldl \
  -o "$output"
