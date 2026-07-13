# Call For Review: Goal5303 X-HD County-ZCTA ArcGIS Bounded Fixture

Date: 2026-07-09

Please strictly review Goal5303.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5303_county_zcta_arcgis_bounded_fixture.py
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/manifest.json
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/dtl_cnty_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/uszipcode_arcgis_bounded.wkt
tests/goal5303_xhd_county_zcta_arcgis_bounded_fixture_test.py
history/internal_docs/goal5303_xhd_county_zcta_arcgis_bounded_fixture_result_2026-07-09.md
```

Relevant prior evidence:

```text
history/internal_docs/goal5301_xhd_non_graphics_dataset_provenance_result_2026-07-09.md
history/internal_docs/goal5302_xhd_census_tiger_source_resolution_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5301_non_graphics_dataset_provenance_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5302_census_tiger_source_resolution_plan_2026-07-09.json
.codex_tmp/xhd_author_repo/expr/run_fig5.sh
.codex_tmp/xhd_author_repo/src/loaders/loader.h
src/rtdsl/datasets.py
```

## Scope

Goal5303 is a bounded input-fixture creation goal.

It does:

```text
query name-matched ArcGIS County and ZIP/ZCTA FeatureServer layers;
write small one-geometry-per-line WKT files;
record hashes, feature counts, object ids, sample names, bounding boxes, and
author-loader outer-ring point-count estimates;
document the exact-vs-Level-B claim boundary.
```

It does not:

```text
run POD
run author hd_exec
run RTDL
claim exact paper dataset identity
claim geo correctness
claim Figure 5 reproduction
claim performance
```

## Claims To Check

1. The fixture is correctly labeled Level-B only and not exact paper input.
2. The generated WKT files are one geometry per line and match the manifest
   hashes / line counts / feature counts.
3. The source contract accurately records ArcGIS name-matched services,
   `OBJECTID` ordering, `outSR=4326`, and requested feature counts.
4. The author-loader contract is represented correctly:
   `input_type=wkt`, `n_dims=2`, `normalize=false`, polygon/MULTIPOLYGON
   outer-ring point estimates.
5. The report honestly notes that the bounded fixture is an ingestion /
   conversion smoke, not a geographic representativeness claim. In particular,
   the first County OBJECTIDs are Alabama counties and the first ZIP/ZCTA
   OBJECTIDs are Alaska ZCTAs.
6. The result does not claim author ingestion, RTDL correctness, Figure 5, exact
   dataset recovery, or performance.
7. The suggested next goal, author `hd_exec` ingestion on POD before RTDL, is
   correct.

## Questions For Reviewer

1. Is ArcGIS name-matched bounded fixture creation a valid next Level-B step
   after Goal5302, or should official TIGER2023 conversion be required first?
2. Does the script keep paper/app semantics out of RTDL core?
3. Are the WKT output and manifest fields sufficient to audit this fixture later?
4. Is the Alabama-vs-Alaska caveat strong enough to prevent a reader from
   treating this as representative geo correctness evidence?
5. Are the tests sufficient for a bounded fixture artifact goal?
6. Should the next goal run author `hd_exec` only first, before any RTDL route?
7. Should Goal5303 close with
   `completed_county_zcta_arcgis_bounded_fixture__level_b_only__no_execution_yet`?

## Requested Verdict Label

```text
approve_goal5303_county_zcta_arcgis_bounded_fixture__level_b_only
```
