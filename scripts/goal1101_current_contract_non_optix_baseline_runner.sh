#!/usr/bin/env bash
set -euo pipefail

# Goal1101 generated runner for same-current-contract non-OptiX baselines.
# Boundary: does not run OptiX, does not create cloud resources, and does not authorize speedup claims.

export PYTHONPATH="${PYTHONPATH:-src:.}"
export RTDL_SOURCE_COMMIT="${RTDL_SOURCE_COMMIT:-$(cat .rtdl_source_commit 2>/dev/null || git rev-parse HEAD 2>/dev/null || true)}"

if [ -z "${RTDL_SOURCE_COMMIT}" ]; then
  echo "RTDL_SOURCE_COMMIT is empty; refusing to collect claim-review baseline artifacts." >&2
  exit 2
fi

OUT_DIR="${OUT_DIR:-docs/reports/goal1101_current_contract_non_optix_baselines}"
mkdir -p "${OUT_DIR}"

echo "Goal1101 current-contract non-OptiX baseline runner"
echo "source_commit=${RTDL_SOURCE_COMMIT}"

echo "Running 1/4: facility recentered CPU oracle baseline"
python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py \
  --scenario facility_service_coverage_recentered \
  --backend cpu_oracle \
  --copies 2500000 \
  --iterations 3 \
  --radius 1.0 \
  --output-json "${OUT_DIR}/facility_recentered_2_5m_cpu_oracle_baseline.json"

echo "Running 2/4: facility recentered Embree baseline"
python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py \
  --scenario facility_service_coverage_recentered \
  --backend embree \
  --copies 2500000 \
  --iterations 3 \
  --radius 1.0 \
  --output-json "${OUT_DIR}/facility_recentered_2_5m_embree_baseline.json"

echo "Running 3/4: Barnes-Hut depth-8 validation Embree baseline"
python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py \
  --scenario barnes_hut_node_coverage \
  --backend embree \
  --body-count 4096 \
  --iterations 3 \
  --radius 0.1 \
  --barnes-tree-depth 8 \
  --hit-threshold 4 \
  --output-json "${OUT_DIR}/barnes_hut_depth8_4096_embree_validation_baseline.json"

echo "Running 4/4: Barnes-Hut depth-8 20M timing Embree baseline"
python3 scripts/goal1101_current_contract_non_optix_baseline_profiler.py \
  --scenario barnes_hut_node_coverage \
  --backend embree \
  --body-count 20000000 \
  --iterations 3 \
  --radius 0.1 \
  --barnes-tree-depth 8 \
  --hit-threshold 4 \
  --skip-validation \
  --output-json "${OUT_DIR}/barnes_hut_depth8_20m_embree_timing_baseline.json"

echo "Goal1101 complete. Review ${OUT_DIR} with an intake gate before any public wording."
