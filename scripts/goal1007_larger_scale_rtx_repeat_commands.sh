#!/usr/bin/env bash
set -euo pipefail

# Goal1007 larger-scale RTX repeat commands.
# Run only from an already-running RTX pod checkout.
# Boundary: does not create cloud resources and does not authorize speedup claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export OPTIX_PREFIX="${OPTIX_PREFIX:-/workspace/vendor/optix-dev-9.0.0}"
export CUDA_PREFIX="${CUDA_PREFIX:-/usr/local/cuda-12.4}"
export NVCC="${NVCC:-${CUDA_PREFIX}/bin/nvcc}"
export RTDL_NVCC="${RTDL_NVCC:-${NVCC}}"
export RTDL_OPTIX_PTX_COMPILER="${RTDL_OPTIX_PTX_COMPILER:-nvcc}"
export RTDL_OPTIX_LIB="${RTDL_OPTIX_LIB:-$(pwd)/build/librtdl_optix.so}"

mkdir -p docs/reports

echo "Goal1007 larger-scale RTX repeats"
nvidia-smi

echo 'Running robot_collision_screening / prepared_pose_flags'
python3 scripts/goal760_optix_robot_pose_flags_phase_profiler.py --mode optix --pose-count 8000000 --obstacle-count 4096 --iterations 7 --input-mode packed_arrays --result-mode pose_count --skip-validation --output-json docs/reports/goal1007_robot_pose_flags_large_rtx.json

echo 'Running outlier_detection / prepared_fixed_radius_density_summary'
python3 scripts/goal757_optix_fixed_radius_prepared_perf.py --copies 400000 --iterations 7 --result-mode threshold_count --skip-validation --output-json docs/reports/goal1007_outlier_dbscan_large_rtx.json

# dbscan_clustering / prepared_fixed_radius_core_flags reuses docs/reports/goal1007_outlier_dbscan_large_rtx.json
echo 'Running facility_knn_assignment / coverage_threshold_prepared'
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario facility_service_coverage --mode optix --copies 800000 --iterations 7 --radius 1.0 --skip-validation --output-json docs/reports/goal1007_facility_service_coverage_large_rtx.json

echo 'Running segment_polygon_hitcount / segment_polygon_hitcount_native_experimental'
python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario segment_polygon_hitcount_prepared --copies 8192 --iterations 7 --mode run --skip-validation --output-json docs/reports/goal1007_segment_polygon_hitcount_large_rtx.json

echo 'Running segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate'
python3 scripts/goal934_prepared_segment_polygon_pair_rows_optix_profiler.py --copies 8192 --iterations 7 --output-capacity 131072 --mode run --skip-validation --output-json docs/reports/goal1007_segment_polygon_anyhit_rows_large_rtx.json

echo 'Running ann_candidate_search / candidate_threshold_prepared'
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario ann_candidate_coverage --mode optix --copies 800000 --iterations 7 --radius 0.2 --skip-validation --output-json docs/reports/goal1007_ann_candidate_coverage_large_rtx.json

python3 scripts/goal1007_larger_scale_rtx_repeat_plan.py \
  --audit-existing \
  --output-json docs/reports/goal1007_larger_scale_rtx_repeat_plan_pod_audit.json \
  --output-md docs/reports/goal1007_larger_scale_rtx_repeat_plan_pod_audit.md
