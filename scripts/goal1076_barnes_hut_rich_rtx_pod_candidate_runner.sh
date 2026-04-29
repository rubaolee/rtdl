#!/usr/bin/env bash
set -euo pipefail

# Goal1076 generated runner for an already-running RTX-class Linux pod.
# Boundary: does not create cloud resources and does not authorize speedup claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-9.0.0}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"

if [ -z "${RTDL_SOURCE_COMMIT}" ]; then
  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-grade artifacts." >&2
  exit 2
fi

mkdir -p docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate
echo "Goal1076 Barnes-Hut rich RTX pod candidate"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
nvidia-smi

echo "Running 1/2: barnes_hut_force_app:correctness_validation"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 1024 --iterations 3 --radius 0.1 --barnes-tree-depth 6 --hit-threshold 4 --output-json docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_validation.json
echo "Completed docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_validation.json"

echo "Running 2/2: barnes_hut_force_app:large_timing_repeat"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 1000000 --iterations 5 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_large_timing.json
echo "Completed docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate/barnes_hut_rich_node_coverage_large_timing.json"

echo "Goal1076 complete. Copy back docs/reports/goal1076_barnes_hut_rich_rtx_pod_candidate before stopping the pod."
