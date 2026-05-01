#!/usr/bin/env bash
set -euo pipefail

# Goal1003 helper for an already-running RTX-class Linux pod.
# It does not create cloud resources, does not contain credentials, and does
# not authorize performance claims. Run from the RTDL checkout root.
# Boundary: does not authorize performance claims.

OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-8.0.0}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12.4}"
NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
REPORT_DIR="${REPORT_DIR:-docs/reports}"

export PYTHONPATH="${PYTHONPATH:-src:.}"
export OPTIX_PREFIX
export CUDA_PREFIX
export NVCC
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"

mkdir -p "${REPORT_DIR}"

echo "Goal1003 RTX pod grouped execution"
echo "repo=$(pwd)"
echo "optix_prefix=${OPTIX_PREFIX}"
echo "cuda_prefix=${CUDA_PREFIX}"
echo "nvcc=${NVCC}"
echo "rtdl_optix_lib=${RTDL_OPTIX_LIB}"
echo

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi is missing. Use an RTX-class NVIDIA GPU pod image." >&2
  exit 2
fi
nvidia-smi

if [ ! -x "${NVCC}" ]; then
  echo "nvcc is missing or not executable at ${NVCC}." >&2
  exit 2
fi

if [ ! -f "${OPTIX_PREFIX}/include/optix.h" ]; then
  echo "OptiX SDK header missing at ${OPTIX_PREFIX}/include/optix.h." >&2
  echo "Use driver-compatible OptiX headers before running the grouped batch." >&2
  exit 2
fi

PYTHONPATH=src:. python3 scripts/goal763_rtx_cloud_bootstrap_check.py \
  --output-json "${REPORT_DIR}/goal763_rtx_cloud_bootstrap_check.json"

python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_pose_flags \
  --output-json "${REPORT_DIR}/goal761_group_a_robot_summary.json"

python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_fixed_radius_density_summary \
  --only prepared_fixed_radius_core_flags \
  --output-json "${REPORT_DIR}/goal761_group_b_fixed_radius_summary.json"

python3 scripts/goal761_rtx_cloud_run_all.py \
  --only prepared_db_session_sales_risk \
  --only prepared_db_session_regional_dashboard \
  --output-json "${REPORT_DIR}/goal761_group_c_database_summary.json"

python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only prepared_gap_summary \
  --only prepared_count_summary \
  --only coverage_threshold_prepared \
  --output-json "${REPORT_DIR}/goal761_group_d_spatial_summary.json"

python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only road_hazard_native_summary_gate \
  --only segment_polygon_hitcount_native_experimental \
  --only segment_polygon_anyhit_rows_prepared_bounded_gate \
  --output-json "${REPORT_DIR}/goal761_group_e_segment_polygon_summary.json"

python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only graph_visibility_edges_gate \
  --output-json "${REPORT_DIR}/goal761_group_f_graph_summary.json"

python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only directed_threshold_prepared \
  --only candidate_threshold_prepared \
  --only node_coverage_prepared \
  --output-json "${REPORT_DIR}/goal761_group_g_prepared_decision_summary.json"

python3 scripts/goal761_rtx_cloud_run_all.py \
  --include-deferred \
  --only polygon_pair_overlap_optix_native_assisted_phase_gate \
  --only polygon_set_jaccard_optix_native_assisted_phase_gate \
  --output-json "${REPORT_DIR}/goal761_group_h_polygon_summary.json"

echo
echo "Grouped RTX run complete. Copy back ${REPORT_DIR}/goal763_rtx_cloud_bootstrap_check.json,"
echo "${REPORT_DIR}/goal761_group_*_summary.json, and all per-app *_rtx.json artifacts before stopping the pod."
