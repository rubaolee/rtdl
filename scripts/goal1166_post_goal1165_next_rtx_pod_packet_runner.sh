#!/usr/bin/env bash
set -euo pipefail

# Goal1166 generated runner for an already-running RTX-class Linux pod.
# Boundary: does not create cloud resources and does not authorize speedup claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIBRARY="${RTDL_OPTIX_LIBRARY:-$(pwd)/build/librtdl_optix.so}"
export LD_LIBRARY_PATH="${CUDA_PREFIX}/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"

if [ -z "${RTDL_SOURCE_COMMIT}" ]; then
  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-grade artifacts." >&2
  exit 2
fi

mkdir -p docs/reports/goal1166_post_goal1165_next_rtx_pod_packet
echo "Goal1166 post-Goal1165 next RTX pod packet"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
nvidia-smi

echo "Running 1/6: ann_candidate_validation"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario ann_candidate_coverage --mode optix --copies 8192 --iterations 3 --radius 0.2 --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_8192_validation.json
echo "Completed docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_8192_validation.json"

echo "Running 2/6: ann_candidate_large_timing"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario ann_candidate_coverage --mode optix --copies 65536 --iterations 7 --radius 0.2 --skip-validation --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_65536_timing.json
echo "Completed docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_65536_timing.json"

echo "Running 3/6: robot_pose_flags_validation"
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 32768 --obstacle-count 64 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_32768_validation.json
echo "Completed docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_32768_validation.json"

echo "Running 4/6: robot_pose_flags_large_timing"
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 262144 --obstacle-count 64 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_262144_timing.json
echo "Completed docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_262144_timing.json"

echo "Running 5/6: jaccard_safe_chunk_validation"
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 1024 --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk1024_validation.json
echo "Completed docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk1024_validation.json"

echo "Running 6/6: jaccard_boundary_diagnostic_small_chunk"
set +e
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 256 --output-json docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk256_diagnostic.json
status=$?
set -e
echo "Boundary diagnostic exit status=${status} (non-zero is expected until fixed)"
echo "Completed docs/reports/goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk256_diagnostic.json"

echo "Goal1166 complete. Copy back docs/reports/goal1166_post_goal1165_next_rtx_pod_packet before stopping the pod."
