# Call for Review - Goals5306-5307 X-HD WaterBodies -> BlockGroups Bounded Gate

Please strictly review Goals5306-5307.

## Files to Review

```text
history/internal_docs/goal5306_xhd_water_bg_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/goal5307_xhd_water_bg_author_rtdl_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5306_water_bg_arcgis_bounded_fixture.py
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/manifest.json
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USADetailedWaterBodies_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USACensusBlockGroupBoundaries_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/author_water_bg_arcgis_bounded.json
Paper-reproduction-apps/x-hd-paper/results/goal5307_raw/rtdl_water_bg_arcgis_bounded_triton_summary_raw_goal5305_runner.json
tests/goal5306_xhd_water_bg_arcgis_bounded_fixture_test.py
tests/goal5307_xhd_water_bg_author_rtdl_gate_test.py
tests/goal5305_xhd_wkt_author_loader_semantics_test.py
```

## Context

Goal5306 creates the second X-HD geo WKT bounded fixture:

```text
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
```

The fixture uses name-matched ArcGIS FeatureServer sources already tracked by
RTDL/RayJoin metadata:

```text
USA_Detailed_Water_Bodies
USA_Census_BlockGroups
```

Goal5307 then runs both author `hd_exec` and RTDL's generic partner route on
that same bounded fixture.

Key evidence:

```text
WaterBodies point count = 124
BlockGroups point count = 894

author HDResult = 72.38665008544922
RTDL HDResult   = 72.38664516014835
abs_diff        = 4.925300871150284e-06
tolerance       = 1e-5
matched         = true
```

RTDL route:

```text
directed_max_of_nearest_distance_2d_partner_columns
partner="triton"
triton_strategy="dense_point_nearest_tiled"
native_engine_row_contract="not_called_partner_reference_only"
```

## Review Questions

1. Does Goal5306 correctly identify and use the ArcGIS source services for the
   second X-HD Figure-5 WKT pair?
2. Is the generated WKT artifact valid one-geometry-per-line WKT suitable for
   the author loader contract?
3. Are the Goal5306 manifest hashes, feature counts, point-count estimates, and
   claim boundaries sufficient for a bounded fixture artifact?
4. Does Goal5307 genuinely run author `hd_exec` on the Goal5306 fixture and
   record author JSON/stdout/stderr evidence?
5. Does Goal5307 genuinely compare RTDL against the author JSON on the same
   bounded WaterBodies->BlockGroups WKT fixture?
6. Is the author/RTDL match (`abs_diff ~= 4.93e-6 <= 1e-5`) sufficient for this
   bounded same-fixture scalar correctness gate?
7. Is the RTDL route properly characterized as a generic partner reference
   route, not the author X-HD RT-core algorithm?
8. Is it acceptable that the raw RTDL execution reused the Goal5305 generic
   partner runner, with Goal5307 wrapping the raw summary into a correctly
   labeled pair-specific summary?
9. Does the packet avoid unauthorized claims: exact paper input recovery,
   Figure 5 reproduction, author RT-core equivalence, performance parity,
   performance ratio, and full paper reproduction?
10. Are the phase timings correctly treated as transparency only, not as an
    author/RTDL performance comparison?
11. Is the geographic limitation stated clearly enough: bounded first-OBJECTID
    fixture, water features in/near Hawaii and block groups in Alabama, not a
    representative or exact paper distribution?
12. Can Goals5306-5307 be marked `implemented_review_pending` and later bundled
    with Goals5302-5305 as evidence that both X-HD Figure-5 WKT pairs now have
    bounded author/RTDL scalar correctness gates?

## Expected Verdict Labels

```text
approve_goals5306_5307_water_bg_bounded_author_rtdl_gate
revise_goals5306_5307_source_fixture_or_claim_boundary
block_goals5306_5307_due_to_invalid_author_rtdl_comparison_or_overclaim
```
