#!/usr/bin/env bash
set -euo pipefail

# Goal1068 generated runner for an already-running RTX-class Linux pod.
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

mkdir -p docs/reports/goal1068_next_rtx_pod_efficiency_batch
echo "Goal1068 next RTX pod efficiency batch"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
nvidia-smi

echo "Running 1/6: facility_knn_assignment:coverage_threshold_prepared:correctness_validation"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 20000 --iterations 10 --radius 1.0 --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_validation.json
echo "Completed docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_validation.json"

echo "Running 2/6: facility_knn_assignment:coverage_threshold_prepared:large_timing_repeat"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 800000 --iterations 7 --radius 1.0 --skip-validation --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_large_timing.json
echo "Completed docs/reports/goal1068_next_rtx_pod_efficiency_batch/facility_coverage_threshold_large_timing.json"

echo "Running 3/6: robot_collision_screening:prepared_pose_flags:correctness_validation"
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_validation.json
echo "Completed docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_validation.json"

echo "Running 4/6: robot_collision_screening:prepared_pose_flags:large_timing_repeat"
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 8000000 --obstacle-count 4096 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_large_timing.json
echo "Completed docs/reports/goal1068_next_rtx_pod_efficiency_batch/robot_prepared_pose_flags_large_timing.json"

echo "Running 5/6: barnes_hut_force_app:node_coverage_prepared:correctness_validation"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 200000 --iterations 3 --radius 10.0 --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_validation.json
echo "Completed docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_validation.json"

echo "Running 6/6: barnes_hut_force_app:node_coverage_prepared:large_timing_repeat"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 1000000 --iterations 7 --radius 10.0 --skip-validation --output-json docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_1m_timing.json
echo "Completed docs/reports/goal1068_next_rtx_pod_efficiency_batch/barnes_hut_node_coverage_1m_timing.json"

echo "Goal1068 complete. Copy back docs/reports/goal1068_next_rtx_pod_efficiency_batch before stopping the pod."
