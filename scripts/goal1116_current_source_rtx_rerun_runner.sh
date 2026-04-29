#!/usr/bin/env bash
set -euo pipefail

# Goal1116 generated runner for an already-running RTX-class Linux pod.
# Boundary: evidence collection only; no public speedup claims are authorized.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-9.0.0}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"

if [ -z "${RTDL_SOURCE_COMMIT}" ]; then
  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-review artifacts." >&2
  exit 2
fi

mkdir -p docs/reports/goal1116_current_source_rtx_rerun_packet
echo "Goal1116 current-source RTX rerun packet"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
nvidia-smi

echo "Running 1/5: facility_knn_assignment:coverage_threshold_prepared_recentered:same_scale_validation_and_timing"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage_recentered --mode optix --copies 2500000 --iterations 5 --radius 1.0 --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json
echo "Completed docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json"

echo "Running 2/5: robot_collision_screening:prepared_pose_flags:correctness_validation"
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json
echo "Completed docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json"

echo "Running 3/5: robot_collision_screening:prepared_pose_flags:large_timing_repeat"
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 8000000 --obstacle-count 4096 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_8m_timing.json
echo "Completed docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_8m_timing.json"

echo "Running 4/5: barnes_hut_force_app:node_coverage_prepared_rich:correctness_validation"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 4096 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json
echo "Completed docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json"

echo "Running 5/5: barnes_hut_force_app:node_coverage_prepared_rich:large_timing_repeat"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 20000000 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json
echo "Completed docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json"

echo "Goal1116 complete. Copy back docs/reports/goal1116_current_source_rtx_rerun_packet before stopping the pod."
