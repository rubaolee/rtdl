# Goal860 Spatial Partial-Ready Gate

Status: `ready_for_review`

This gate is for the two spatial prepared-summary apps only. It requires same-semantics local baselines before the apps can move toward active RTX review, and it still requires a real OptiX phase artifact before any promotion or claim review.

## Summary

- rows checked: `2`
- required valid artifacts: `4`
- required missing artifacts: `0`
- required invalid artifacts: `0`

## Row Status

| App | Path | Status | Required Valid | Required Missing | RTX Artifact |
|---|---|---|---:|---:|---|
| service_coverage_gaps | prepared_gap_summary | ready_for_review | 2 | 0 | valid |
| event_hotspot_screening | prepared_count_summary | ready_for_review | 2 | 0 | valid |

## Details

### service_coverage_gaps / prepared_gap_summary

- claim limit: prepared compact summary only; not nearest-row or whole-app speedup
- RTX artifact: `valid` at `/Users/rl2025/rtdl_python_only/docs/reports/goal811_service_coverage_rtx.json`

- required `cpu_oracle_summary`: `valid`
- required `embree_summary_path`: `valid`
- optional `scipy_baseline_when_available`: `missing`

### event_hotspot_screening / prepared_count_summary

- claim limit: prepared compact summary only; not nearest-row or whole-app speedup
- RTX artifact: `valid` at `/Users/rl2025/rtdl_python_only/docs/reports/goal811_event_hotspot_rtx.json`

- required `cpu_oracle_summary`: `valid`
- required `embree_summary_path`: `valid`
- optional `scipy_baseline_when_available`: `missing`
