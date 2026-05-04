#!/usr/bin/env bash
set -euo pipefail

# Goal1192 six-row public-wording evidence batch runner.
# Intended for RTX-class Linux pods after source archive extraction and
# `make build-optix` have completed. This script does not authorize public
# speedup wording; it only produces artifacts for later intake/review.

OUTDIR="${OUTDIR:-docs/reports/goal1192_public_wording_evidence_batch}"
mkdir -p "${OUTDIR}"

echo "Goal1192 public-wording evidence batch"
date -u
python3 --version || true
nvidia-smi || true

echo "Running 1/12: database_analytics embree baseline"
python3 scripts/goal756_db_prepared_session_perf.py --backend embree --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json "${OUTDIR}/database_compact_summary_embree.json"

echo "Running 2/12: database_analytics optix"
python3 scripts/goal756_db_prepared_session_perf.py --backend optix --scenario sales_risk --copies 30000 --iterations 10 --output-mode compact_summary --strict --output-json "${OUTDIR}/database_compact_summary_optix.json"

echo "Running 3/12: graph visibility embree baseline"
python3 examples/rtdl_graph_analytics_app.py --backend embree --scenario visibility_edges --copies 30000 --output-mode summary > "${OUTDIR}/graph_visibility_edges_embree.json"

echo "Running 4/12: graph visibility optix"
python3 scripts/goal889_graph_visibility_optix_gate.py --copies 30000 --output-mode summary --validation-mode analytic_summary --chunk-copies 0 --strict --output-json "${OUTDIR}/graph_visibility_edges_optix.json"

echo "Running 5/12: road hazard embree baseline"
python3 examples/rtdl_road_hazard_screening.py --backend embree --copies 20000 --output-mode summary > "${OUTDIR}/road_hazard_native_summary_embree.json"

echo "Running 6/12: road hazard optix"
python3 scripts/goal933_prepared_segment_polygon_optix_profiler.py --scenario road_hazard_prepared_summary --copies 20000 --iterations 5 --mode run --output-json "${OUTDIR}/road_hazard_native_summary_optix.json"

echo "Running 7/12: polygon pair embree candidate baseline"
python3 examples/rtdl_polygon_pair_overlap_area_rows.py --backend embree --copies 20000 --output-mode summary > "${OUTDIR}/polygon_pair_candidate_discovery_embree.json"

echo "Running 8/12: polygon pair optix candidate discovery"
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app pair_overlap --mode optix --copies 20000 --output-mode summary --validation-mode analytic_summary --chunk-copies 100 --output-json "${OUTDIR}/polygon_pair_candidate_discovery_optix.json"

echo "Running 9/12: polygon jaccard embree candidate baseline"
python3 examples/rtdl_polygon_set_jaccard.py --backend embree --copies 8192 --output-mode summary > "${OUTDIR}/polygon_jaccard_safe_chunk_embree.json"

echo "Running 10/12: polygon jaccard optix candidate discovery"
python3 scripts/goal877_polygon_overlap_optix_phase_profiler.py --app jaccard --mode optix --copies 8192 --output-mode summary --validation-mode analytic_summary --chunk-copies 1024 --output-json "${OUTDIR}/polygon_jaccard_safe_chunk_optix.json"

echo "Running 11/12: hausdorff embree baseline"
python3 examples/rtdl_hausdorff_distance_app.py --backend embree --copies 200000 --embree-result-mode directed_summary --hausdorff-threshold 0.4 > "${OUTDIR}/hausdorff_threshold_prepared_embree.json"

echo "Running 12/12: hausdorff optix"
python3 scripts/goal887_prepared_decision_phase_profiler.py --scenario hausdorff_threshold --mode optix --copies 200000 --iterations 10 --radius 0.4 --output-json "${OUTDIR}/hausdorff_threshold_prepared_optix.json"

tar -czf "${OUTDIR}.tgz" "${OUTDIR}"
sha256sum "${OUTDIR}.tgz" > "${OUTDIR}.tgz.sha256"

echo "Goal1192 batch complete"
echo "result_tgz=${OUTDIR}.tgz"
echo "result_sha=${OUTDIR}.tgz.sha256"
