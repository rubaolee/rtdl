#!/usr/bin/env bash
set -uo pipefail

# Goal1141 consolidated RTX pod runner.
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

mkdir -p docs/reports/goal1141_rtx_single_session_bundle
STATUS_FILE="docs/reports/goal1141_rtx_single_session_bundle/goal1141_status.tsv"
LOG_FILE="docs/reports/goal1141_rtx_single_session_bundle/goal1141_runner.log"
printf "label\tstatus\trc\tutc\n" > "${STATUS_FILE}"
exec > >(tee -a "${LOG_FILE}") 2>&1
echo "Goal1141 RTX single-session pod bundle"
echo "source_commit=${RTDL_SOURCE_COMMIT}"
echo "git_head=$(git rev-parse HEAD 2>/dev/null || true)"
date -u +"utc_start=%Y-%m-%dT%H:%M:%SZ"
nvidia-smi || true

run_step() {
  local label="$1"
  shift
  echo "BEGIN ${label}"
  date -u +"${label}_utc_start=%Y-%m-%dT%H:%M:%SZ"
  "$@"
  local rc=$?
  local status=ok
  if [ "${rc}" -ne 0 ]; then
    status=failed
  fi
  printf "%s\t%s\t%s\t%s\n" "${label}" "${status}" "${rc}" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "${STATUS_FILE}"
  echo "END ${label} status=${status} rc=${rc}"
  return 0
}

run_step setup_1 bash -lc 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config'
run_step setup_2 python3 scripts/goal763_rtx_cloud_bootstrap_check.py --skip-tests --output-json docs/reports/goal1141_rtx_single_session_bundle/bootstrap_preflight.json
run_step setup_3 python3 scripts/goal763_rtx_cloud_bootstrap_check.py --output-json docs/reports/goal1141_rtx_single_session_bundle/bootstrap_full.json

run_step entry_1_goal1116_facility_knn_assignment_same_scale_validation_and_timing python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage_recentered --mode optix --copies 2500000 --iterations 5 --radius 1.0 --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json
run_step entry_2_goal1116_robot_collision_screening_correctness_validation python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 4096 --obstacle-count 256 --iterations 3 --input-mode python_objects --result-mode pose_flags --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_validation.json
run_step entry_3_goal1116_robot_collision_screening_large_timing_repeat python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 8000000 --obstacle-count 4096 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/robot_prepared_pose_flags_8m_timing.json
run_step entry_4_goal1116_barnes_hut_force_app_correctness_validation python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 4096 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_4096_validation.json
run_step entry_5_goal1116_barnes_hut_force_app_large_timing_repeat python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario barnes_hut_node_coverage --mode optix --body-count 20000000 --iterations 3 --radius 0.1 --barnes-tree-depth 8 --hit-threshold 4 --skip-validation --output-json docs/reports/goal1116_current_source_rtx_rerun_packet/barnes_hut_depth8_20m_timing.json
run_step entry_6_goal1135_database_analytics_compact_summary python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario all --copies 20000 --iterations 5 --output-mode compact_summary --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/database_analytics_compact_summary.json
run_step entry_7_goal1135_graph_visibility_edges_gate python3 scripts/goal889_graph_visibility_optix_gate.py --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/graph_visibility_edges_gate.json
run_step entry_8_goal1135_road_hazard_native_summary_count python3 scripts/goal888_road_hazard_native_optix_gate.py --copies 20000 --output-mode summary --strict --output-json docs/reports/goal1135_changed_path_rtx_pod/road_hazard_native_summary_count.json
run_step entry_9_goal1135_polygon_pair_overlap_phase_gate python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1135_changed_path_rtx_pod/polygon_pair_overlap_phase_gate.json
run_step entry_10_goal1135_polygon_set_jaccard_phase_gate python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 20 --output-json docs/reports/goal1135_changed_path_rtx_pod/polygon_set_jaccard_phase_gate.json
run_step entry_11_goal1135_hausdorff_threshold_phase_gate python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 20000 --iterations 5 --radius 0.4 --output-json docs/reports/goal1135_changed_path_rtx_pod/hausdorff_threshold_phase_gate.json

date -u +"utc_end=%Y-%m-%dT%H:%M:%SZ"
echo "Goal1141 complete. Review ${STATUS_FILE} and copy back docs/reports/goal1141_rtx_single_session_bundle, docs/reports/goal1116_current_source_rtx_rerun_packet, and docs/reports/goal1135_changed_path_rtx_pod before stopping the pod."
if grep -q $'\tfailed\t' "${STATUS_FILE}"; then
  echo "One or more Goal1141 steps failed; keep the pod only if same-pod targeted retry is useful." >&2
  exit 1
fi
