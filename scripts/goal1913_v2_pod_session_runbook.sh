#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
OPTIX_PREFIX="${OPTIX_PREFIX:-/root/vendor/optix-sdk}"
OUT_DIR="${OUT_DIR:-docs/reports/goal1903_v2_partner_pod_batch}"
RUN_PREFLIGHT="${RUN_PREFLIGHT:-1}"
RUN_BATCH="${RUN_BATCH:-1}"
RUN_ACCEPTANCE="${RUN_ACCEPTANCE:-1}"
RUN_MANIFEST="${RUN_MANIFEST:-1}"
RUN_READINESS="${RUN_READINESS:-1}"

RTDL_PYTHONPATH="src:."
if [[ -n "${PYTHONPATH:-}" ]]; then
  RTDL_PYTHONPATH="${PYTHONPATH}:${RTDL_PYTHONPATH}"
fi

log() {
  printf '[goal1913] %s\n' "$*"
}

run_step() {
  local name="$1"
  shift
  log "BEGIN ${name}"
  "$@"
  log "END ${name}"
}

log "repo=$(pwd)"
log "commit=$(git rev-parse HEAD)"
log "python=$(${PYTHON_BIN} --version 2>&1)"
log "optix_prefix=${OPTIX_PREFIX}"
log "out_dir=${OUT_DIR}"
if command -v nvidia-smi >/dev/null 2>&1; then
  log "nvidia-smi follows"
  nvidia-smi
else
  log "nvidia-smi missing"
fi

if [[ "${RUN_PREFLIGHT}" == "1" ]]; then
  run_step "local non-pod preflight" env PYTHONPATH="${RTDL_PYTHONPATH}" "${PYTHON_BIN}" \
    scripts/goal1908_v2_local_preflight.py \
    --output docs/reports/goal1913_pre_pod_local_preflight.json
fi

if [[ "${RUN_BATCH}" == "1" ]]; then
  run_step "RTX pod batch" env \
    PYTHONPATH="${PYTHONPATH:-}" \
    OUT_DIR="${OUT_DIR}" \
    OPTIX_PREFIX="${OPTIX_PREFIX}" \
    PYTHON_BIN="${PYTHON_BIN}" \
    bash scripts/goal1903_v2_partner_pod_batch_runner.sh
fi

if [[ "${RUN_ACCEPTANCE}" == "1" ]]; then
  run_step "strict post-pod acceptance" env PYTHONPATH="${RTDL_PYTHONPATH}" "${PYTHON_BIN}" \
    scripts/goal1905_v2_partner_pod_batch_acceptance.py \
    --output docs/reports/goal1905_v2_partner_pod_batch_acceptance.json
fi

if [[ "${RUN_MANIFEST}" == "1" ]]; then
  run_step "post-pod artifact manifest" env PYTHONPATH="${RTDL_PYTHONPATH}" "${PYTHON_BIN}" \
    scripts/goal1916_v2_post_pod_artifact_manifest.py \
    --output docs/reports/goal1916_v2_post_pod_artifact_manifest.json
fi

if [[ "${RUN_READINESS}" == "1" ]]; then
  run_step "readiness aggregation" env PYTHONPATH="${RTDL_PYTHONPATH}" "${PYTHON_BIN}" \
    scripts/goal1911_v2_readiness_aggregator.py \
    --output docs/reports/goal1911_v2_readiness_aggregator.json
fi

log "complete"
log "next: send docs/handoff/GOAL1912_POST_POD_EXTERNAL_REVIEW_TEMPLATE_2026-05-13.md to external reviewers if acceptance passed"
