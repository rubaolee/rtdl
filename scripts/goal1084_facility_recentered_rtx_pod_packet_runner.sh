#!/usr/bin/env bash
set -euo pipefail

# Goal1084 generated runner for an already-running RTX-class Linux pod.
# Boundary: does not create cloud resources and does not authorize speedup claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-9.0.0}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(git rev-parse HEAD 2>/dev/null || cat .rtdl_source_commit 2>/dev/null || true)}"

if [ -z "${RTDL_SOURCE_COMMIT}" ]; then
  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-grade artifacts." >&2
  exit 2
fi

mkdir -p docs/reports/goal1084_facility_recentered_rtx_pod_packet
echo "Goal1084 facility recentered RTX pod packet"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
nvidia-smi

echo "Running 1/1: facility_knn_assignment:coverage_threshold_prepared_recentered:same_scale_validation_and_timing"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage_recentered --mode optix --copies 2500000 --iterations 5 --radius 1.0 --output-json docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json
echo "Completed docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json"

echo "Goal1084 complete. Copy back docs/reports/goal1084_facility_recentered_rtx_pod_packet before stopping the pod."
