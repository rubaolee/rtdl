#!/usr/bin/env bash
set -euo pipefail

# Goal5057 one-command POD runtime path:
# bootstrap compatible CUDA/Numba env, then run the strict Goal5052 smoke.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

ENV_JSON="${RTDL_V2144_POD_ENV_JSON:-history/internal_docs/goal5057_v2144_pod_env_bootstrap_result.json}"
EXPORTS_SH="${RTDL_V2144_POD_ENV_EXPORTS:-history/internal_docs/goal5057_v2144_pod_env_exports.sh}"
SMOKE_JSON="${1:-history/internal_docs/goal5052_v2144_public_api_pod_smoke_result.json}"

RTDL_V2144_POD_ENV_EXPORTS="${EXPORTS_SH}" \
  bash scripts/goal5057_v2144_pod_env_bootstrap.sh "${ENV_JSON}"

# shellcheck disable=SC1090
source "${EXPORTS_SH}"

export PYTHONPATH="${PYTHONPATH:-src:.}"
export RTDL_OPTIX_LIBRARY="${RTDL_OPTIX_LIBRARY:-$(pwd)/build/librtdl_optix.so}"

bash scripts/goal5052_v2144_public_api_pod_smoke_runner.sh "${SMOKE_JSON}"

echo "Goal5057 strict POD smoke complete: ${SMOKE_JSON}"
