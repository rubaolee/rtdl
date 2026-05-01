# Goal975 Linux PostGIS Remaining Baselines

Status: `ok`

PostGIS is an external same-semantics baseline. These artifacts do not authorize public RTX speedup claims.

- Linux host: `lestat-lx1` / `192.168.1.20`
- PostgreSQL/PostGIS: PostgreSQL `16`, PostGIS `3.4.2`, GEOS `3.12.1`
- database: `rtdl_postgis`
- copies: `256`
- repeats: `3`
- artifacts: `5`

## Result

Goal975 collected the remaining PostGIS baselines that were still missing after Goal974:

- `road_hazard_screening / road_hazard_native_summary_gate`
- `segment_polygon_hitcount / segment_polygon_hitcount_native_experimental`
- `segment_polygon_anyhit_rows / segment_polygon_anyhit_rows_prepared_bounded_gate`
- `polygon_pair_overlap_area_rows / polygon_pair_overlap_optix_native_assisted_phase_gate`
- `polygon_set_jaccard / polygon_set_jaccard_optix_native_assisted_phase_gate`

After copying the artifacts back to the macOS working tree and regenerating Goal836/Goal971:

- Goal836 valid artifacts: `42 / 50`
- Goal836 invalid artifacts: `0`
- Goal836 remaining missing artifacts: `8`
- Goal971 strict same-semantics baseline-complete RTX rows: `11 / 17`
- Goal971 public speedup claims authorized: `0`

Remaining gaps are no longer PostGIS gaps. They are optional SciPy/reference-neighbor baselines, graph OptiX baselines, and the segment/polygon OptiX bounded pair-row artifact.

| Artifact |
|---|
| `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_road_hazard_screening_road_hazard_native_summary_gate_postgis_when_available_2026-04-23.json` |
| `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_segment_polygon_hitcount_segment_polygon_hitcount_native_experimental_postgis_when_available_2026-04-23.json` |
| `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_segment_polygon_anyhit_rows_segment_polygon_anyhit_rows_prepared_bounded_gate_postgis_when_available_for_same_pair_semantics_2026-04-23.json` |
| `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_polygon_pair_overlap_area_rows_polygon_pair_overlap_optix_native_assisted_phase_gate_postgis_when_available_for_same_unit_cell_contract_2026-04-23.json` |
| `/Users/rl2025/rtdl_python_only/docs/reports/goal835_baseline_polygon_set_jaccard_polygon_set_jaccard_optix_native_assisted_phase_gate_postgis_when_available_for_same_unit_cell_contract_2026-04-23.json` |

## Verification

Commands run:

```bash
ssh lestat-lx1 'psql -d rtdl_postgis -Atqc "select postgis_full_version();"'
rsync -az /Users/rl2025/rtdl_python_only/ lestat-lx1:/home/lestat/rtdl_goal975_postgis/
ssh lestat-lx1 'cd /home/lestat/rtdl_goal975_postgis && PYTHONPATH=src:. python3 scripts/goal975_linux_postgis_remaining_baselines.py --db-name rtdl_postgis --copies 256 --repeats 3'
PYTHONPATH=src:. python3 scripts/goal836_rtx_baseline_readiness_gate.py --output-json docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.json --output-md docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.md
PYTHONPATH=src:. python3 -m unittest tests.goal975_linux_postgis_remaining_baselines_test tests.goal974_remaining_local_baselines_test tests.goal971_post_goal969_baseline_speedup_review_package_test tests.goal846_active_rtx_claim_gate_test
```
