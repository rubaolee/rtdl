# X-HD Geo Level-B Bounded Packet - Goals5302-5307

Date: 2026-07-09

## Status

```text
implemented_review_pending
```

This packet consolidates the X-HD geo/WKT line from source resolution through
bounded author/RTDL scalar correctness for the two Figure-5 WKT pair names:

```text
dtl_cnty.wkt -> uszipcode.wkt
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
```

Both pair names now have bounded author/RTDL scalar matches on generated
ArcGIS WKT fixtures. This is **Level-B bounded same-fixture evidence**, not
exact paper input recovery and not Figure 5 reproduction.

## Goal Chain

| Goal | Scope | Status |
|---|---|---|
| Goal5302 | Resolve X-HD geo source candidates and author WKT contract | implemented / review pending |
| Goal5303 | Build bounded County->ZCTA ArcGIS WKT fixture | implemented / review pending |
| Goal5304 | Run author `hd_exec` on County->ZCTA fixture | implemented / review pending |
| Goal5305 | Run RTDL generic partner route on County->ZCTA fixture | implemented / review pending |
| Goal5306 | Build bounded WaterBodies->BlockGroups ArcGIS WKT fixture | implemented / review pending |
| Goal5307 | Run author + RTDL on WaterBodies->BlockGroups fixture | implemented / review pending |

## Author WKT Contract

Goal5302 records the relevant author contract:

```text
input_type = wkt
n_dims = 2
normalize = false
POLYGON / MULTIPOLYGON: outer ring vertices
LINESTRING / MULTILINESTRING: line vertices
POINT: one point
```

The RTDL app-owned WKT loader was extended to match this point-stream contract.

## Pair 1 - County -> ZCTA

Fixture:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/dtl_cnty_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/uszipcode_arcgis_bounded.wkt
```

Source:

```text
ArcGIS USA_Census_Counties, first 3 OBJECTIDs
ArcGIS USA_ZIP_Code_Areas_anaylsis, first 5 OBJECTIDs
```

Point counts:

```text
County = 38,034
ZCTA   = 50,272
```

Result:

```text
Author HDResult = 65.44752502441406
RTDL HDResult   = 65.44751976280666
abs diff        = 5.2616073986655465e-06 <= 1e-5
matched         = true
```

RTDL route:

```text
directed_max_of_nearest_distance_2d_partner_columns
partner = triton
triton_strategy = dense_point_nearest_tiled
native_engine_row_contract = not_called_partner_reference_only
```

Primary evidence:

```text
history/internal_docs/goal5303_xhd_county_zcta_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/goal5304_xhd_county_zcta_author_ingestion_result_2026-07-09.md
history/internal_docs/goal5305_xhd_county_zcta_rtdl_partner_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json
```

## Pair 2 - WaterBodies -> BlockGroups

Fixture:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USADetailedWaterBodies_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USACensusBlockGroupBoundaries_arcgis_bounded.wkt
```

Source:

```text
ArcGIS USA_Detailed_Water_Bodies, first 5 OBJECTIDs
ArcGIS USA_Census_BlockGroups, first 5 OBJECTIDs
```

Point counts:

```text
WaterBodies = 124
BlockGroups = 894
```

Result:

```text
Author HDResult = 72.38665008544922
RTDL HDResult   = 72.38664516014835
abs diff        = 4.925300871150284e-06 <= 1e-5
matched         = true
```

RTDL route:

```text
directed_max_of_nearest_distance_2d_partner_columns
partner = triton
triton_strategy = dense_point_nearest_tiled
native_engine_row_contract = not_called_partner_reference_only
```

Primary evidence:

```text
history/internal_docs/goal5306_xhd_water_bg_arcgis_bounded_fixture_result_2026-07-09.md
history/internal_docs/goal5307_xhd_water_bg_author_rtdl_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json
```

## What This Proves

```text
The app-owned RTDL WKT front door, author hd_exec WKT loader, and RTDL generic
partner directed max-nearest route agree on scalar HDResult for bounded
same-fixture examples covering both X-HD Figure-5 WKT pair names.
```

This is stronger than scaffold/provenance-only work because both author and
RTDL run on the same generated WKT files for both pair names.

## What This Does Not Prove

This packet does **not** prove:

```text
exact paper WKT input recovery;
Figure 5 reproduction;
full-paper reproduction;
author X-HD RT-core algorithm equivalence;
denominator-aligned author/RTDL performance;
performance parity;
geographic representativeness of the bounded fixtures.
```

Why not:

- the fixtures use first-OBJECTID bounded ArcGIS selections, not author file
  hashes or exact dataset provenance;
- the generated features are not geographically paired samples;
- RTDL uses a generic partner reference route, not the author RT-core
  implementation;
- author `Running.AvgTime` and RTDL route/total phases are not the same
  denominator.

## Immediate Next Decision

The next work should move from bounded correctness to dataset provenance:

```text
Goal5308: decide exact/full-public geo input path.
```

That goal should answer:

1. Are exact author WKT files obtainable or already present anywhere?
2. If exact files are unavailable, what public reconstruction is defensible?
3. What evidence would be enough to upgrade from Level-B bounded to a
   Figure-5-like public reproduction?
4. Which phase denominators must be aligned before any performance ratio is
   allowed?

Until that decision exists, bounded geo evidence must stay bounded.
