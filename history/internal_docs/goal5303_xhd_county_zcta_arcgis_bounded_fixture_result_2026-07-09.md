# Goal5303 X-HD County-ZCTA ArcGIS Bounded Fixture Result

Date: 2026-07-09

## Verdict

`completed_county_zcta_arcgis_bounded_fixture__level_b_only__no_execution_yet`

## Purpose

Goal5303 turns the Goal5302 County-ZCTA source plan into an actual bounded WKT
input artifact.

This is still not an author/RTDL comparison goal. It does not run POD, does not
run author `hd_exec`, does not run RTDL, and does not claim geo correctness or a
paper figure.

## New Files

Created:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5303_county_zcta_arcgis_bounded_fixture.py
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/dtl_cnty_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/uszipcode_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/manifest.json
tests/goal5303_xhd_county_zcta_arcgis_bounded_fixture_test.py
```

## Source Contract

The fixture uses the name-matched ArcGIS FeatureServer sources already tracked
by prior RTDL/RayJoin asset metadata:

```text
USA_Census_Counties
USA_ZIP_Code_Areas_anaylsis
```

Query contract:

```text
f = geojson
where = 1=1
orderByFields = OBJECTID
outSR = 4326
county feature count = 3
zipcode feature count = 5
```

This deliberately creates a small bounded fixture. It does not prove that the
ArcGIS services are the author's exact X-HD paper inputs, and it does not prove
the service year / simplification / export path used by the paper.

## Generated Artifact

Manifest:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/manifest.json
```

County output:

```text
path = Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/dtl_cnty_arcgis_bounded.wkt
bytes = 943098
sha256 = 204551e901d3695cffcf0701993e037dcd805494d0e6518c3ec6e3f01f7526aa
feature_count = 3
line_count = 3
geometry_types = Polygon:2, MultiPolygon:1
object_ids = [1, 2, 3]
sample_names = Autauga County, Baldwin County, Barbour County
outer_ring_point_count_author_loader_estimate = 38034
bbox = [-88.0291319999999, -85.048825, 30.2209285380001, 32.7082130000001]
```

ZIP/ZCTA output:

```text
path = Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded/uszipcode_arcgis_bounded.wkt
bytes = 1168282
sha256 = 5cc9ee7fee44348f1ba1110d1e6e07bb490b762df1c5e5e5a3e55b8cf9903e91
feature_count = 5
line_count = 5
geometry_types = MultiPolygon:4, Polygon:1
object_ids = [1, 2, 3, 4, 5]
sample_names = 00001, 00002, 00003, 00004, 00005
outer_ring_point_count_author_loader_estimate = 50272
bbox = [-160.431152, -141.002465, 55.6387556, 68.501329]
```

Important caveat:

```text
The first County OBJECTIDs are Alabama counties, while the first ZIP/ZCTA
OBJECTIDs are Alaska ZCTAs. This fixture is useful for author-loader and RTDL
WKT ingestion / conversion checks, but it is not a geographic representativeness
or paper-distribution claim.
```

## Author Loader Contract Covered

The builder writes one WKT geometry per line, matching the author's WKT loader
mode from Goal5302:

```text
input_type = wkt
n_dims = 2
normalize = false
POLYGON / MULTIPOLYGON outer rings provide the point-count estimate
```

The artifact includes both `POLYGON` and `MULTIPOLYGON` lines. That makes it a
useful bounded smoke for the author Boost WKT path before larger official TIGER
or ArcGIS exports are attempted.

## Comparison Readiness

The manifest intentionally records:

```text
author_hd_exec_ready = false
rtdl_route_ready = false
```

Reason:

```text
This goal creates a bounded input fixture and metadata only; author/RTDL
execution should be a separate gate.
```

First author command shape for the next goal:

```text
./bin/hd_exec -input1 <county_wkt> -input2 <zipcode_wkt> -input_type wkt -n_dims 2 -variant rt -execution gpu -normalize=false -json <summary.json>
```

## Claim Boundary

Allowed summary:

```text
Goal5303 creates a bounded ArcGIS County-ZCTA WKT fixture and metadata for the
X-HD geo path. It is a Level-B ingestion/conversion artifact, not an exact paper
dataset and not an author/RTDL comparison.
```

Forbidden summaries:

```text
X-HD geo inputs are recovered.
County-ZCTA exact paper inputs are recovered.
Geo Figure 5 is reproduced.
The fixture proves geo correctness.
The fixture is representative of the paper's full US geo distribution.
Author/RTDL performance can now be compared.
```

## Validation

Commands run:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5303_county_zcta_arcgis_bounded_fixture.py
py -m unittest tests.goal5303_xhd_county_zcta_arcgis_bounded_fixture_test
```

Result:

```text
Ran 3 tests in 0.026s
OK
```

The Windows Python environment printed the known noisy prefix warning:

```text
Could not find platform independent libraries <prefix>
```

The tests passed.

## Next Recommended Goal

Goal5304 should run the author binary on this bounded WKT fixture on POD before
any RTDL route:

```text
1. preflight POD through scripts/current_pod_ssh.py;
2. upload the two WKT files and manifest;
3. run author hd_exec with input_type=wkt, n_dims=2, normalize=false;
4. download and record the author JSON;
5. only if author ingestion succeeds, decide whether to run RTDL on the same
   bounded fixture.
```

If author ingestion fails, the next step is to fix the WKT conversion contract,
not to run RTDL.
