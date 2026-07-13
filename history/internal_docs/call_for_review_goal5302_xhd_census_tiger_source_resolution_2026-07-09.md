# Call For Review: Goal5302 X-HD Census/TIGER Source Resolution

Date: 2026-07-09

Please strictly review Goal5302.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5302_census_tiger_source_resolution_plan_2026-07-09.json
tests/goal5302_xhd_census_tiger_source_resolution_test.py
history/internal_docs/goal5302_xhd_census_tiger_source_resolution_result_2026-07-09.md
```

Relevant prior/current evidence:

```text
.codex_tmp/xhd_author_repo/expr/run_fig5.sh
.codex_tmp/xhd_author_repo/src/loaders/loader.h
Paper-reproduction-apps/x-hd-paper/results/xhd_author_log_workload_manifest_goal5175_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
src/rtdsl/datasets.py
```

External sources checked:

```text
https://www.census.gov/geographies/mapping-files/2023/geo/tiger-line-file.html
https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html
https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
```

## Scope

Goal5302 is a source-resolution and conversion-planning goal. It should not be judged as an execution result.

It does not:

```text
download full datasets
create WKT input artifacts
run POD
run author hd_exec
run RTDL
claim correctness
claim performance
```

## Claims To Check

1. Author `run_fig5.sh` geo contract is accurately extracted:
   - `dtl_cnty.wkt -> uszipcode.wkt`
   - `USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt`
   - `lakes.bz2.wkt -> parks.bz2.wkt`
   - `input_type=wkt`, `n_dims=2`, `normalize=false`
2. Author WKT loader semantics are correctly represented:
   - POLYGON/MULTIPOLYGON outer rings only;
   - LINESTRING/MULTILINESTRING vertices;
   - POINT single point;
   - bad geometry aborts.
3. Official source probes are correctly interpreted:
   - national COUNTY and ZCTA520 candidates exist;
   - BG should be treated as state shards from the evidence here;
   - AREAWATER should be treated as county-FIPS shards from the evidence here.
4. County-ZCTA is correctly selected as first executable Level-B geo candidate.
5. The report does not promote TIGER/ArcGIS candidates to exact paper inputs.
6. The report does not claim any geo author/RTDL comparison or performance ratio.
7. `Goal5303_county_zcta_conversion_probe_plan_or_bounded_fixture` is the correct next goal.

## Questions For Reviewer

1. Is the author geo contract accurately extracted from the author scripts and logs?
2. Does the WKT loader contract capture the conversion hazards that must be tested before execution?
3. Are the official TIGER2023 URL probes sufficient for a source-resolution plan?
4. Should the first executable County-ZCTA path use official TIGER2023 files, ArcGIS name-matched services, or both as competing Level-B candidates?
5. Is it correct to defer WaterBodies/BlockGroups until County-ZCTA is resolved?
6. Are the tests sufficient for a source-resolution goal?
7. Should Goal5302 close with `completed_census_tiger_source_resolution__county_zcta_first__no_execution_yet`?

## Requested Verdict Label

```text
approve_goal5302_census_tiger_source_resolution__county_zcta_first
```
