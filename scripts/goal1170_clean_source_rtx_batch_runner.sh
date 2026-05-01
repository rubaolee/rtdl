#!/usr/bin/env bash
set -euo pipefail

# Goal1170 clean-source RTX batch runner.
# Run from a clean pushed checkout on an already-running RTX-class pod.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIBRARY="${RTDL_OPTIX_LIBRARY:-$(pwd)/build/librtdl_optix.so}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-${RTDL_OPTIX_LIBRARY}}"
export LD_LIBRARY_PATH="${CUDA_PREFIX}/lib64:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(git rev-parse HEAD)}"

if [ -n "$(git status --short)" ]; then
  echo "Refusing claim-grade run: git working tree is dirty." >&2
  git status --short >&2
  exit 2
fi

mkdir -p "docs/reports/goal1170_clean_source_rtx_claim_grade_batch"
echo "Goal1170 clean-source RTX claim-grade batch"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
nvidia-smi
python3 scripts/goal1171_clean_source_rtx_pod_preflight.py --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1171_preflight.json --output-md docs/reports/goal1170_clean_source_rtx_claim_grade_batch/goal1171_preflight.md

echo "Running 1/8: database_compact_summary"
python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/database_compact_summary.json
echo "Completed docs/reports/goal1170_clean_source_rtx_claim_grade_batch/database_compact_summary.json"

echo "Running 2/8: graph_visibility_edges"
python3 scripts/goal889_graph_visibility_optix_gate.py --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/graph_visibility_edges.json
echo "Completed docs/reports/goal1170_clean_source_rtx_claim_grade_batch/graph_visibility_edges.json"

echo "Running 3/8: road_hazard_native_summary"
python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/road_hazard_native_summary.json
echo "Completed docs/reports/goal1170_clean_source_rtx_claim_grade_batch/road_hazard_native_summary.json"

echo "Running 4/8: polygon_pair_candidate_discovery"
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/polygon_pair_candidate_discovery.json
echo "Completed docs/reports/goal1170_clean_source_rtx_claim_grade_batch/polygon_pair_candidate_discovery.json"

echo "Running 5/8: polygon_jaccard_safe_chunk"
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 512 --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/polygon_jaccard_safe_chunk.json
echo "Completed docs/reports/goal1170_clean_source_rtx_claim_grade_batch/polygon_jaccard_safe_chunk.json"

echo "Running 6/8: hausdorff_threshold_prepared"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 20000 --iterations 10 --radius 0.4 --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/hausdorff_threshold_prepared.json
echo "Completed docs/reports/goal1170_clean_source_rtx_claim_grade_batch/hausdorff_threshold_prepared.json"

echo "Running 7/8: ann_candidate_large_timing_replacement"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario ann_candidate_coverage --mode optix --copies 65536 --iterations 7 --radius 0.2 --skip-validation --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/ann_candidate_65536_timing.json
echo "Completed docs/reports/goal1170_clean_source_rtx_claim_grade_batch/ann_candidate_65536_timing.json"

echo "Running 8/8: robot_pose_count_large_timing_replacement"
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 262144 --obstacle-count 64 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1170_clean_source_rtx_claim_grade_batch/robot_pose_count_262144_timing.json
echo "Completed docs/reports/goal1170_clean_source_rtx_claim_grade_batch/robot_pose_count_262144_timing.json"

echo "Goal1170 batch complete. Copy back docs/reports/goal1170_clean_source_rtx_claim_grade_batch."
