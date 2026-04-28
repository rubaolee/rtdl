#!/usr/bin/env bash
set -euo pipefail

# Goal1053 generated pod-side runner for an already-running RTX-class Linux pod.
# Boundary: does not create cloud resources and does not authorize speedup claims.

OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-8.0.0}"
CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12.4}"
NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
REPORT_DIR="${REPORT_DIR:-docs/reports/goal1052_post_goal1048_cloud_batch}"

export PYTHONPATH="${PYTHONPATH:-src:.}"
export OPTIX_PREFIX
export CUDA_PREFIX
export NVCC
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"

if [ -z "${RTDL_SOURCE_COMMIT}" ]; then
  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-grade artifacts." >&2
  exit 2
fi

mkdir -p "${REPORT_DIR}"
echo "Goal1053 post-Goal1048 RTX cloud batch runner"
echo "repo=$(pwd)"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
echo "report_dir=${REPORT_DIR}"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi is missing. Use an RTX-class NVIDIA GPU pod image." >&2
  exit 2
fi
nvidia-smi

python3 scripts/goal763_rtx_cloud_bootstrap_check.py --output-json docs/reports/goal1052_post_goal1048_cloud_batch/goal763_rtx_cloud_bootstrap_check.json

echo "Running 1/11: facility_knn_assignment:coverage_threshold_prepared"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 20000 --iterations 10 --radius 1.0 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/coverage_threshold_prepared.json
echo "Completed facility_knn_assignment:coverage_threshold_prepared; copy back docs/reports/goal1052_post_goal1048_cloud_batch/coverage_threshold_prepared.json"

echo "Running 2/11: robot_collision_screening:prepared_pose_flags"
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_pose_flags.json
echo "Completed robot_collision_screening:prepared_pose_flags; copy back docs/reports/goal1052_post_goal1048_cloud_batch/prepared_pose_flags.json"

echo "Running 3/11: database_analytics:prepared_db_session_sales_risk"
python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_db_session_sales_risk.json
echo "Completed database_analytics:prepared_db_session_sales_risk; copy back docs/reports/goal1052_post_goal1048_cloud_batch/prepared_db_session_sales_risk.json"

echo "Running 4/11: database_analytics:prepared_db_session_regional_dashboard"
python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario regional_dashboard --copies 20000 --iterations 10 --output-mode compact_summary --strict --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_db_session_regional_dashboard.json
echo "Completed database_analytics:prepared_db_session_regional_dashboard; copy back docs/reports/goal1052_post_goal1048_cloud_batch/prepared_db_session_regional_dashboard.json"

echo "Running 5/11: graph_analytics:graph_visibility_edges_gate"
python3 scripts/goal889_graph_visibility_optix_gate.py --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1052_post_goal1048_cloud_batch/graph_visibility_edges_gate.json
echo "Completed graph_analytics:graph_visibility_edges_gate; copy back docs/reports/goal1052_post_goal1048_cloud_batch/graph_visibility_edges_gate.json"

echo "Running 6/11: event_hotspot_screening:prepared_count_summary"
python3 scripts/goal811_spatial_optix_summary_phase_profiler.py --scenario event_hotspot_screening --mode optix --copies 20000 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/prepared_count_summary.json
echo "Completed event_hotspot_screening:prepared_count_summary; copy back docs/reports/goal1052_post_goal1048_cloud_batch/prepared_count_summary.json"

echo "Running 7/11: road_hazard_screening:road_hazard_native_summary_gate"
python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json docs/reports/goal1052_post_goal1048_cloud_batch/road_hazard_native_summary_gate.json
echo "Completed road_hazard_screening:road_hazard_native_summary_gate; copy back docs/reports/goal1052_post_goal1048_cloud_batch/road_hazard_native_summary_gate.json"

echo "Running 8/11: polygon_pair_overlap_area_rows:polygon_pair_overlap_optix_native_assisted_phase_gate"
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/polygon_pair_overlap_optix_native_assisted_phase_gate.json
echo "Completed polygon_pair_overlap_area_rows:polygon_pair_overlap_optix_native_assisted_phase_gate; copy back docs/reports/goal1052_post_goal1048_cloud_batch/polygon_pair_overlap_optix_native_assisted_phase_gate.json"

echo "Running 9/11: polygon_set_jaccard:polygon_set_jaccard_optix_native_assisted_phase_gate"
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/polygon_set_jaccard_optix_native_assisted_phase_gate.json
echo "Completed polygon_set_jaccard:polygon_set_jaccard_optix_native_assisted_phase_gate; copy back docs/reports/goal1052_post_goal1048_cloud_batch/polygon_set_jaccard_optix_native_assisted_phase_gate.json"

echo "Running 10/11: hausdorff_distance:directed_threshold_prepared"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 20000 --iterations 10 --radius 0.4 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/directed_threshold_prepared.json
echo "Completed hausdorff_distance:directed_threshold_prepared; copy back docs/reports/goal1052_post_goal1048_cloud_batch/directed_threshold_prepared.json"

echo "Running 11/11: barnes_hut_force_app:node_coverage_prepared"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 200000 --iterations 10 --radius 10.0 --output-json docs/reports/goal1052_post_goal1048_cloud_batch/node_coverage_prepared.json
echo "Completed barnes_hut_force_app:node_coverage_prepared; copy back docs/reports/goal1052_post_goal1048_cloud_batch/node_coverage_prepared.json"

echo "Goal1053 batch complete. Copy back ${REPORT_DIR} before stopping the pod."
