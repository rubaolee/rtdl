#!/usr/bin/env bash
set -euo pipefail

STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-900}"
WARMUPS="${WARMUPS:-3}"
REPEATS="${REPEATS:-15}"
OUTPUT_DIR="${OUTPUT_DIR:-docs/reports/goal2327_rayjoin_pod_perf}"
LSI_STREAM="${LSI_STREAM:-}"
PIP_STREAM="${PIP_STREAM:-}"

log() {
  printf '[goal2327][%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2
}

run_step() {
  local label="$1"
  shift
  log "START ${label}"
  timeout "${STEP_TIMEOUT_SECONDS}" "$@"
  log "DONE ${label}"
}

if [[ -z "${RTDL_OPTIX_LIBRARY:-}" ]]; then
  log "RTDL_OPTIX_LIBRARY must point to build/librtdl_optix.so"
  exit 2
fi

mkdir -p "${OUTPUT_DIR}"
log "repo=$(pwd)"
log "commit=$(git rev-parse HEAD)"
log "python=$("${PYTHON_BIN:-python3}" --version 2>&1)"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | tee "${OUTPUT_DIR}/gpu.txt"
fi

run_step "fixture prepared_optix lsi count" \
  "${PYTHON_BIN:-python3}" examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
    --workload lsi --execution-route prepared_optix --result-mode count --no-rows \
    > "${OUTPUT_DIR}/fixture_lsi_prepared_count.json"

run_step "fixture prepared_optix pip rows-no-materialization" \
  "${PYTHON_BIN:-python3}" examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py \
    --workload pip --execution-route prepared_optix --result-mode rows --no-rows \
    > "${OUTPUT_DIR}/fixture_pip_prepared_rows_nomaterialize.json"

if [[ -n "${LSI_STREAM}" && -n "${PIP_STREAM}" ]]; then
  run_step "same-query prepared comparison streams" \
    "${PYTHON_BIN:-python3}" scripts/goal2292_rayjoin_current_prepared_comparison.py \
      --lsi-stream "${LSI_STREAM}" \
      --pip-stream "${PIP_STREAM}" \
      --warmups "${WARMUPS}" \
      --repeats "${REPEATS}" \
      --output "${OUTPUT_DIR}/same_query_prepared_comparison.json"
else
  log "LSI_STREAM/PIP_STREAM not provided; skipped same-query RayJoin stream replay"
fi

cat > "${OUTPUT_DIR}/claim_boundary.json" <<'JSON'
{
  "full_rayjoin_reproduction": false,
  "rtdl_beats_rayjoin_claim_authorized": false,
  "paper_scale_perf_claim_authorized": false,
  "whole_app_speedup_claim_authorized": false,
  "v2_0_release_authorized": false,
  "requires_external_review_before_public_claim": true
}
JSON

run_step "summarize artifacts" \
  "${PYTHON_BIN:-python3}" scripts/goal2327_rayjoin_pod_artifact_summary.py \
    --input-dir "${OUTPUT_DIR}" \
    --output "${OUTPUT_DIR}/summary.md"

log "wrote ${OUTPUT_DIR}"
