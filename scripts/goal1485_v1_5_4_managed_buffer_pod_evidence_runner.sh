#!/usr/bin/env bash
set -euo pipefail

RESULT_DIR="${RESULT_DIR:-docs/reports/goal1485_v1_5_4_managed_buffer_pod_results_2026-05-07}"
mkdir -p "${RESULT_DIR}"

echo "Goal1485 v1.5.4 managed-buffer pod evidence runner"
echo "result_dir=${RESULT_DIR}"

{
  echo "Goal1485 pod environment"
  date -u
  uname -a
  git rev-parse HEAD || true
  git status --short || true
  nvidia-smi || true
  python3 --version || true
  command -v nvcc || true
  nvcc --version || true
} | tee "${RESULT_DIR}/goal1485_pod_environment.log"

export PYTHONPATH="${PYTHONPATH:-src:.}"

python3 scripts/goal1485_v1_5_4_managed_buffer_pod_evidence_packet.py \
  --allocation-method "${ALLOCATION_METHOD:-cuda_device_alloc}" \
  --buffer-kind "${BUFFER_KIND:-rtdl_device_resident}" \
  --device "${RTDL_DEVICE:-cuda:0}" \
  --host-to-device-transfers "${HOST_TO_DEVICE_TRANSFERS:-0}" \
  --device-to-host-transfers "${DEVICE_TO_HOST_TRANSFERS:-0}" \
  --device-residency-observed \
  --measured-on-real-nvidia \
  --hardware-identity "${HARDWARE_IDENTITY:-$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -n 1 || true)}" \
  --backend-version "${BACKEND_VERSION:-$(nvcc --version 2>/dev/null | tail -n 1 || true)}" \
  --measurement-scope "${MEASUREMENT_SCOPE:-goal1485_real_nvidia_managed_buffer_allocation_probe}" \
  --json-out "${RESULT_DIR}/goal1485_managed_buffer_pod_evidence_2026-05-07.json" \
  --md-out "${RESULT_DIR}/goal1485_managed_buffer_pod_evidence_2026-05-07.md" \
  2>&1 | tee "${RESULT_DIR}/goal1485_managed_buffer_pod_evidence.log"

echo "Goal1485 pod evidence runner complete"
echo "result_dir=${RESULT_DIR}"
