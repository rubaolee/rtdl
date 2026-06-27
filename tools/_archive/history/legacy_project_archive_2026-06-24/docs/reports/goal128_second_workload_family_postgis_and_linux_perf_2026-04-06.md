# Goal 128 Report: Second Workload Family PostGIS And Linux Perf

Date: 2026-04-06
Status: accepted

## Summary

Goal 127 made `segment_polygon_anyhit_rows` a real RTDL workload family in the
codebase. Goal 128 prepares the next closure layer:

- PostGIS-backed correctness checking
- Linux large-row backend performance reporting

That external-evidence step is now complete on the accepted Linux host `lx1`.

## Local additions

Added:

- `src/rtdsl/goal128_segment_polygon_anyhit_postgis.py`
- `tests/goal128_segment_polygon_anyhit_postgis_test.py`

The new module provides:

- `run_postgis_segment_polygon_anyhit_rows(...)`
- `run_goal128_segment_polygon_anyhit_postgis_validation(...)`
- `run_goal128_segment_polygon_anyhit_linux_large_perf(...)`
- markdown/json artifact writers for both result families

## Validation

Local regression after the schema-fix pass:

- `PYTHONPATH=src:. python3 -m unittest tests.goal128_segment_polygon_anyhit_postgis_test tests.goal10_workloads_test tests.baseline_contracts_test tests.rtdsl_language_test tests.test_core_quality`
  - `109` tests
  - `OK`
  - `1` skipped
  - same existing local Mac `geos_c` linker noise appears before the skipped case

Linux/PostGIS execution on `lx1`:

- `PYTHONPATH=src:. python3 scripts/goal128_segment_polygon_anyhit_postgis_validation.py --copies 64 --backends cpu,embree,optix,vulkan --db-name rtdl_postgis --output-dir build/goal128_postgis_x64`
- `PYTHONPATH=src:. python3 scripts/goal128_segment_polygon_anyhit_linux_large_perf.py --db-name rtdl_postgis --perf-iterations 3 --output-dir build/goal128_linux_large_perf`

## PostGIS validation result

Validated dataset:

- `derived/br_county_subset_segment_polygon_tiled_x64`

Result:

- PostGIS rows: `704`
- PostGIS SHA256:
  - `e97b0f49c4a5f024bdda672737ddd83c88a05f054ce0486919af3b9a6edf6210`
- parity vs PostGIS:
  - `cpu`: `True`
  - `embree`: `True`
  - `optix`: `True`
  - `vulkan`: `True`

Timing on the validation row:

- PostGIS: `0.003241 s`
- CPU: `0.010849 s`
- Embree: `0.010000 s`
- OptiX: `0.006234 s`
- Vulkan: `0.003213 s`

## Linux large-scale performance

PostGIS-backed rows stayed parity-clean on:

- `x64`
- `x256`
- `x512`
- `x1024`

Key large rows:

| Dataset | PostGIS (s) | CPU (s) | Embree (s) | OptiX (s) | Vulkan (s) | All Parity |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `derived/br_county_subset_segment_polygon_tiled_x64` | 0.003253 | 0.010866 | 0.010686 | 0.006354 | 0.003331 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x256` | 0.015174 | 0.008591 | 0.012124 | 0.007125 | 0.007383 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x512` | 0.030755 | 0.016822 | 0.014740 | 0.014660 | 0.014616 | `True` |
| `derived/br_county_subset_segment_polygon_tiled_x1024` | 0.054076 | 0.033509 | 0.030137 | 0.036671 | 0.029602 | `True` |

Prepared-path means on the audited prepared rows:

- `x64`
  - Embree current `0.000943 s`, prepared reuse `0.000408 s`
  - OptiX current `0.002511 s`, prepared reuse `0.000369 s`
- `x256`
  - Embree current `0.003588 s`, prepared reuse `0.001627 s`
  - OptiX current `0.003443 s`, prepared reuse `0.001506 s`

## Interpretation

The result is stronger than the earlier local-only state:

- `segment_polygon_anyhit_rows` is externally checked against PostGIS
- Linux large-row backend timings are now published
- the candidate-index line that helped `segment_polygon_hitcount` also gives
  this second workload family a strong backend story

Current honest reading:

- correctness is strong across `cpu`, `embree`, `optix`, and `vulkan`
- on the larger audited rows, all four RTDL backends are competitive with or
  faster than PostGIS
- Vulkan remains acceptable under the current product policy:
  correct and not very slow, without claiming fully optimized flagship status

## Artifacts

- [goal128 PostGIS x64 JSON](/Users/rl2025/rtdl_python_only/docs/reports/goal128_second_workload_family_postgis_and_linux_perf_artifacts_2026-04-06/postgis_x64/goal128_segment_polygon_anyhit_postgis_validation.json)
- [goal128 PostGIS x64 Markdown](/Users/rl2025/rtdl_python_only/docs/reports/goal128_second_workload_family_postgis_and_linux_perf_artifacts_2026-04-06/postgis_x64/goal128_segment_polygon_anyhit_postgis_validation.md)
- [goal128 Linux large-perf JSON](/Users/rl2025/rtdl_python_only/docs/reports/goal128_second_workload_family_postgis_and_linux_perf_artifacts_2026-04-06/linux_large_perf/goal128_segment_polygon_anyhit_linux_large_perf.json)
- [goal128 Linux large-perf Markdown](/Users/rl2025/rtdl_python_only/docs/reports/goal128_second_workload_family_postgis_and_linux_perf_artifacts_2026-04-06/linux_large_perf/goal128_segment_polygon_anyhit_linux_large_perf.md)

So Goal 128 is now closed as the external-evidence layer for the second v0.2
workload family.
