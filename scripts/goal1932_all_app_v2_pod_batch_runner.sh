#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${OUT_DIR:-docs/reports/goal1932_all_app_v2_pod_batch}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
FIXED_REPEAT="${FIXED_REPEAT:-5}"
FIXED_QUERY_COUNT="${FIXED_QUERY_COUNT:-}"
FIXED_SEARCH_COUNT="${FIXED_SEARCH_COUNT:-}"
SEGMENT_ITERATIONS="${SEGMENT_ITERATIONS:-5}"
SEGMENT_COUNTS="${SEGMENT_COUNTS:-512,2048}"
ROBOT_REPEAT="${ROBOT_REPEAT:-5}"
ROBOT_POSE_COUNT="${ROBOT_POSE_COUNT:-4096}"
ROBOT_OBSTACLE_COUNT="${ROBOT_OBSTACLE_COUNT:-256}"
POLYGON_COPIES="${POLYGON_COPIES:-4096}"
DB_COPIES="${DB_COPIES:-20000}"
GRAPH_COPIES="${GRAPH_COPIES:-20000}"
PARTNERS="${PARTNERS:-cupy,torch}"
STEP_TIMEOUT_SECONDS="${STEP_TIMEOUT_SECONDS:-2700}"

mkdir -p "$OUT_DIR"
export PYTHONPATH="${PYTHONPATH:-src:.}"

run_step() {
  local name="$1"
  shift
  echo "[goal1932] $(date -Iseconds) start ${name}" | tee -a "$OUT_DIR/progress.log"
  if [[ "$STEP_TIMEOUT_SECONDS" == "0" ]]; then
    "$@"
  else
    timeout --preserve-status "${STEP_TIMEOUT_SECONDS}s" "$@"
  fi
  echo "[goal1932] $(date -Iseconds) done ${name}" | tee -a "$OUT_DIR/progress.log"
}

fixed_radius_args=(
  --apps facility_knn_assignment,hausdorff_distance,ann_candidate_search,outlier_detection,dbscan_clustering,barnes_hut_force_app
  --partners "$PARTNERS"
  --repeat "$FIXED_REPEAT"
  --output "$OUT_DIR/goal1925_fixed_radius_family_v2_partner_perf_pod.json"
)
if [[ -n "$FIXED_QUERY_COUNT" ]]; then
  fixed_radius_args+=(--query-count-override "$FIXED_QUERY_COUNT")
fi
if [[ -n "$FIXED_SEARCH_COUNT" ]]; then
  fixed_radius_args+=(--search-count-override "$FIXED_SEARCH_COUNT")
fi

run_step "goal1930_matrix_refresh" \
  "$PYTHON_BIN" scripts/goal1930_all_app_v2_matrix.py \
    --output-json "$OUT_DIR/goal1930_all_app_v2_matrix.json" \
    --output-md "$OUT_DIR/goal1930_all_app_v2_matrix.md"

run_step "goal1925_fixed_radius_six_app_family" \
  "$PYTHON_BIN" scripts/goal1925_fixed_radius_family_v2_partner_perf.py \
    "${fixed_radius_args[@]}"

run_step "goal1928_robot_collision_pose_flags" \
  "$PYTHON_BIN" scripts/goal1928_robot_collision_v2_partner_perf.py \
    --pose-count "$ROBOT_POSE_COUNT" \
    --obstacle-count "$ROBOT_OBSTACLE_COUNT" \
    --partners "$PARTNERS" \
    --repeat "$ROBOT_REPEAT" \
    --output "$OUT_DIR/goal1928_robot_collision_v2_partner_perf_pod.json"

IFS=',' read -r -a segment_counts <<< "$SEGMENT_COUNTS"
for segment_count in "${segment_counts[@]}"; do
  segment_count="$(echo "$segment_count" | tr -d '[:space:]')"
  if [[ -z "$segment_count" ]]; then
    continue
  fi
  run_step "goal1856_segment_polygon_anyhit_rows_${segment_count}" \
    "$PYTHON_BIN" scripts/goal1856_segment_polygon_v2_partner_perf.py \
      --count "$segment_count" \
      --iterations "$SEGMENT_ITERATIONS" \
      --partners "$PARTNERS" \
      --output "$OUT_DIR/goal1856_segment_polygon_v2_partner_perf_pod_current_${segment_count}.json"
done

run_step "control_polygon_pair_overlap_area_rows" \
  "$PYTHON_BIN" scripts/goal877_polygon_overlap_optix_phase_profiler.py \
    --app pair_overlap \
    --mode optix \
    --copies "$POLYGON_COPIES" \
    --output-mode summary \
    --validation-mode analytic_summary \
    --output-json "$OUT_DIR/control_polygon_pair_overlap_area_rows_optix.json"

run_step "control_polygon_set_jaccard" \
  "$PYTHON_BIN" scripts/goal877_polygon_overlap_optix_phase_profiler.py \
    --app jaccard \
    --mode optix \
    --copies "$POLYGON_COPIES" \
    --output-mode summary \
    --validation-mode analytic_summary \
    --output-json "$OUT_DIR/control_polygon_set_jaccard_optix.json"

run_step "control_database_analytics" \
  "$PYTHON_BIN" scripts/goal756_db_prepared_session_perf.py \
    --backend optix \
    --scenario all \
    --copies "$DB_COPIES" \
    --iterations 3 \
    --output-mode compact_summary \
    --output-json "$OUT_DIR/control_database_analytics_optix.json"

run_step "control_graph_analytics" \
  "$PYTHON_BIN" scripts/goal982_graph_same_scale_timing_repair.py \
    --copies "$GRAPH_COPIES" \
    --repeats 3 \
    --output-json "$OUT_DIR/control_graph_analytics_embree.json" \
    --output-md "$OUT_DIR/control_graph_analytics_embree.md"

run_step "goal1931_current_analysis_refresh" \
  "$PYTHON_BIN" scripts/goal1931_current_all_app_v18_v2_perf_analysis.py \
    --output-json "$OUT_DIR/goal1931_current_all_app_v18_v2_perf_analysis.json" \
    --output-md "$OUT_DIR/goal1931_current_all_app_v18_v2_perf_analysis.md"

echo "[goal1932] $(date -Iseconds) all steps completed" | tee -a "$OUT_DIR/progress.log"
