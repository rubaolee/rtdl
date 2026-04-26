# Goal862 Spatial RTX Collection Packet

This packet requests real RTX collection only for the two spatial prepared-summary apps. It does not promote them automatically and does not authorize a public speedup claim.

## Summary

- source Goal860 status: `ready_for_review`
- rows packaged: `2`

## One-Shot Runner Example

```bash
python3 scripts/goal769_rtx_pod_one_shot.py --only service_coverage_gaps --only event_hotspot_screening --include-deferred
```

## App Packets

### event_hotspot_screening / prepared_count_summary

- gate status: `ready_for_review`
- claim scope: prepared OptiX fixed-radius count traversal for hotspot summaries
- non-claim: not a whole-app hotspot-screening speedup claim and not a neighbor-row output claim
- claim limit: prepared compact summary only; not nearest-row or whole-app speedup
- RTX output artifact: `docs/reports/goal811_event_hotspot_rtx.json`

Required local baselines:
- `cpu_oracle_summary`: `valid` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_cpu_oracle_summary_2026-04-23.json`
- `embree_summary_path`: `valid` at `/Users/rl2025/rtdl_python_only/docs/reports/goal919_event_hotspot_same_scale_embree_baseline_2026-04-25.json`

Optional local baselines:
- `scipy_baseline_when_available`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_event_hotspot_screening_prepared_count_summary_scipy_baseline_when_available_2026-04-23.json`

RTX command:
```bash
python3 scripts/goal811_spatial_optix_summary_phase_profiler.py --scenario event_hotspot_screening --mode optix --copies 20000 --output-json docs/reports/goal811_event_hotspot_rtx.json
```

- reason deferred: active after artifact intake
- activation gate: already active after artifact intake

### service_coverage_gaps / prepared_gap_summary

- gate status: `ready_for_review`
- claim scope: prepared OptiX fixed-radius threshold traversal for coverage-gap summaries
- non-claim: not a whole-app service coverage speedup claim and not a nearest-clinic row-output claim
- claim limit: prepared compact summary only; not nearest-row or whole-app speedup
- RTX output artifact: `docs/reports/goal811_service_coverage_rtx.json`

Required local baselines:
- `cpu_oracle_summary`: `valid` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_cpu_oracle_summary_2026-04-23.json`
- `embree_summary_path`: `valid` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_embree_summary_path_2026-04-23.json`

Optional local baselines:
- `scipy_baseline_when_available`: `missing` at `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_service_coverage_gaps_prepared_gap_summary_scipy_baseline_when_available_2026-04-23.json`

RTX command:
```bash
python3 scripts/goal811_spatial_optix_summary_phase_profiler.py --scenario service_coverage_gaps --mode optix --copies 20000 --output-json docs/reports/goal811_service_coverage_rtx.json
```

- reason deferred: active after artifact intake
- activation gate: already active after artifact intake
