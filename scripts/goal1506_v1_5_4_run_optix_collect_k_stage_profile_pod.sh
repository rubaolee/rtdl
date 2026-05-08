#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

COUNTS="${COUNTS:-4097 65537 131072}"
REPEATS="${REPEATS:-5}"
OPTIX_PREFIX_ARG=()
if [[ -n "${OPTIX_PREFIX:-}" ]]; then
  OPTIX_PREFIX_ARG=("OPTIX_PREFIX=${OPTIX_PREFIX}")
fi

echo "== RTDL Goal1506 OptiX collect-k stage profile pod runner =="
echo "repo: $ROOT"
echo "commit: $(git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "counts: $COUNTS"
echo "repeats: $REPEATS"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,driver_version --format=csv,noheader || true
fi

PYTHONPATH=src:. python3 scripts/goal1508_v1_5_4_optix_collect_k_tiled_preflight.py \
  --counts $COUNTS

make build-optix "${OPTIX_PREFIX_ARG[@]}"

PYTHONPATH=src:. python3 scripts/goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py \
  --library build/librtdl_optix.so \
  --counts $COUNTS \
  --repeats "$REPEATS"

PYTHONPATH=src:. python3 -m unittest \
  tests.goal1506_v1_5_4_optix_collect_k_stage_profile_plan_test \
  tests.goal1505_v1_5_4_optix_collect_k_evidence_summary_test \
  tests.goal1504_v1_5_4_optix_collect_k_tiled_overflow_probe_test \
  tests.goal1503_v1_5_4_optix_collect_k_scaling_evidence_test \
  tests.goal1502_v1_5_4_optix_collect_k_blackwell_bounds_evidence_test

echo "Goal1506 stage profile artifacts:"
echo "  docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.json"
echo "  docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.md"
echo "  docs/reports/goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.jsonl"
echo "Goal1508 tiled preflight artifacts:"
echo "  docs/reports/goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08.json"
echo "  docs/reports/goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08.md"
