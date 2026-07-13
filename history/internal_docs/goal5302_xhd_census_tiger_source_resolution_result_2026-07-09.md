# Goal5302 X-HD Census/TIGER Source Resolution Result

Date: 2026-07-09

## Verdict

`completed_census_tiger_source_resolution__county_zcta_first__no_execution_yet`

## Purpose

Goal5302 turns Goal5301's "Census/TIGER is the best next non-graphics target" decision into a concrete source-resolution plan.

This is still not an execution goal. It does not download full datasets, does not run POD, does not run author `hd_exec`, and does not run RTDL.

## New Artifact

Created:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5302_census_tiger_source_resolution_plan_2026-07-09.json
```

## Author Contract Evidence

The author `run_fig5.sh` geo workload uses:

```text
dtl_cnty.wkt -> uszipcode.wkt
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
lakes.bz2.wkt -> parks.bz2.wkt

input_type = wkt
n_dims = 2
normalize = false
```

The first executable candidate is:

```text
dtl_cnty.wkt -> uszipcode.wkt
```

because it is the smaller Census/TIGER-like pair and both source sides have directly probe-verified public-source candidates.

## Author WKT Loader Contract

The author WKT loader accepts:

```text
MULTIPOLYGON
POLYGON
LINESTRING
MULTILINESTRING
POINT
```

Important conversion detail:

```text
POLYGON / MULTIPOLYGON: author loader emits outer ring vertices only.
LINESTRING / MULTILINESTRING: author loader emits line vertices.
POINT: author loader emits one point.
```

Therefore a shapefile-to-WKT converter is not enough by itself. The generated WKT must be one geometry per line, and its author-loader point counts must match the author-log point counts before any correctness or performance comparison is allowed.

## Official Source Probe

HEAD probes, no large downloads:

```text
COUNTY:
  https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip
  status = 200
  content_length = 83,451,409

ZCTA520:
  https://www2.census.gov/geo/tiger/TIGER2023/ZCTA520/tl_2023_us_zcta520.zip
  status = 200
  content_length = 528,313,293

BG national:
  https://www2.census.gov/geo/tiger/TIGER2023/BG/tl_2023_us_bg.zip
  status = timeout
  interpretation = do not assume a national single-file entry from this probe

BG state shards:
  https://www2.census.gov/geo/tiger/TIGER2023/BG/tl_2023_01_bg.zip
  status = 200
  https://www2.census.gov/geo/tiger/TIGER2023/BG/tl_2023_06_bg.zip
  status = 200

AREAWATER county shard:
  https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_01001_areawater.zip
  status = 200
```

## Source Resolution

### `dtl_cnty.wkt` / USCounty

Preferred Level-B candidate:

```text
TIGER2023 national COUNTY shapefile
```

Alternative name-matched source:

```text
ArcGIS USA Census Counties item/service already tracked by RTDL RayJoin assets
```

Still unresolved:

```text
exact author source year
whether author used TIGER direct or ArcGIS export
coordinate precision
one-line WKT geometry formatting
author-loader point count match
```

### `uszipcode.wkt` / USZipcode

Preferred Level-B candidate:

```text
TIGER2023 national ZCTA520 shapefile
```

Alternative name-matched source:

```text
ArcGIS USA ZIP Code Boundaries item/service already tracked by RTDL RayJoin assets
```

Still unresolved:

```text
ZCTA vs commercial ZIP boundary distinction
exact author source year
coordinate precision
author-loader point count match
```

### `USADetailedWaterBodies.wkt` / USWater

Preferred name-matched source:

```text
ArcGIS USA Detailed Water Bodies
```

Official-Census alternative:

```text
TIGER2023 AREAWATER county-FIPS shards
```

This pair is deferred until County-ZCTA is resolved unless review directs otherwise.

### `USACensusBlockGroupBoundaries.wkt` / USCensus

Preferred official source pattern:

```text
TIGER2023 state-based BG shapefiles
```

Alternative name-matched source:

```text
ArcGIS USA Census Block Group Boundaries item/service already tracked by RTDL RayJoin assets
```

This pair is also deferred until County-ZCTA is resolved unless review directs otherwise.

## Decision

Next implementation goal should not be a performance run. It should be:

```text
Goal5303_county_zcta_conversion_probe_plan_or_bounded_fixture
```

Scope:

```text
Choose official TIGER2023 or ArcGIS name-matched source for County-ZCTA.
Define shapefile/export -> one-line WKT conversion.
Record source archive hash, WKT hash, point count, bounding box, and Gini.
Fail closed if author-loader point count materially differs from author log.
Only then run author/RTDL comparison.
```

## Claim Boundary

Allowed summary:

```text
Goal5302 resolves concrete source candidates and conversion contracts for the Census/TIGER-like X-HD geo path; County-ZCTA is the recommended first executable Level-B candidate, but no geo input artifact or comparison exists yet.
```

Forbidden summaries:

```text
Census/TIGER exact paper inputs are recovered.
USCounty/USZipcode comparison is ready to run.
Geo Figure 5 is reproduced.
ArcGIS or TIGER source identity is proven exact.
Performance ratio is available.
```

## Validation

Added:

```text
tests/goal5302_xhd_census_tiger_source_resolution_test.py
```

The test verifies:

- author geo pair contract;
- author WKT loader semantics;
- HEAD-probed official source candidates;
- BG / AREAWATER shard interpretation;
- first executable candidate and forbidden claims.
