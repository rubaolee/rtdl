#!/usr/bin/env bash
set -euo pipefail

TRANSACTION=${1:?usage: goal5773_home_preserve.sh TRANSACTION_ROOT}
SOURCE="$TRANSACTION/source"
RESULT="$TRANSACTION/result_v2/RESULT.json"
OUTPUT="$TRANSACTION/GOAL5773_EXECUTION_SOURCE.tar.gz"

test -d "$SOURCE"
test -f "$SOURCE/build/librtdl_optix.so"
test -f "$RESULT"
test ! -e "$OUTPUT"

cd "$SOURCE"
tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
  --exclude=.git --exclude=build --exclude=__pycache__ --exclude='*.pyc' \
  -cf - . | gzip -n > "$OUTPUT"

sha256sum "$OUTPUT" "$SOURCE/build/librtdl_optix.so" "$RESULT"
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader
