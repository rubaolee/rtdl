# Goal5306 - X-HD WaterBodies -> BlockGroups ArcGIS Bounded Fixture Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5306 creates a bounded ArcGIS WKT fixture for the second X-HD Figure-5 geo
pair:

```text
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
```

This is an input-fixture goal only. It does not run author `hd_exec`, does not
run RTDL, and does not claim exact paper input recovery, Figure 5 reproduction,
geo correctness, or performance.

## New Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5306_water_bg_arcgis_bounded_fixture.py
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USADetailedWaterBodies_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USACensusBlockGroupBoundaries_arcgis_bounded.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/manifest.json
tests/goal5306_xhd_water_bg_arcgis_bounded_fixture_test.py
```

## Source Contract

The fixture uses ArcGIS FeatureServer sources already tracked by RTDL/RayJoin
dataset metadata:

```text
USA_Detailed_Water_Bodies
USA_Census_BlockGroups
```

Query contract:

```text
where = 1=1
orderByFields = OBJECTID
outSR = 4326
f = geojson
water feature count = 5
blockgroup feature count = 5
```

This is name-matched public-source evidence. It is not proof of the author's
exact paper input files, source year, export process, or coordinate precision.

## Generated Artifact

Manifest:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/manifest.json
```

WaterBodies output:

```text
path = Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USADetailedWaterBodies_arcgis_bounded.wkt
bytes = 3742
sha256 = 3dda7b9df0655e0070f129625c4cfb7ab9cb40b22c8b71da3994faf0283c1dcb
feature_count = 5
line_count = 5
geometry_types = Polygon:5
object_ids = [1, 2, 3, 4, 5]
outer_ring_point_count_author_loader_estimate = 124
bbox = [-158.039698966938, -157.730386142575, 21.2749468266754, 21.3849224255351]
```

BlockGroups output:

```text
path = Paper-reproduction-apps/x-hd-paper/data/generated/goal5306_arcgis_water_bg_bounded/USACensusBlockGroupBoundaries_arcgis_bounded.wkt
bytes = 26682
sha256 = 01ec10a1cdd3520f3bcc5742a6c7a6430c7e9dbe45f170ec35a5d70d4f7455b9
feature_count = 5
line_count = 5
geometry_types = Polygon:5
object_ids = [1, 2, 3, 4, 5]
sample_labels = [010010201001, 010010201002, 010010202001, 010010202002, 010010203001]
outer_ring_point_count_author_loader_estimate = 894
bbox = [-86.5104237431699, -86.4515247259963, 32.4497330783256, 32.5051650900736]
```

Important caveat:

```text
The first WaterBodies OBJECTIDs are in/near Hawaii, while the first BlockGroup
OBJECTIDs are in Alabama. This fixture is useful for author-loader and RTDL WKT
ingestion / conversion checks, but it is not geographic representativeness or
paper-distribution evidence.
```

## Author Loader Contract Covered

The builder writes one WKT geometry per line and preserves the author loader
contract from Goal5302:

```text
input_type = wkt
n_dims = 2
normalize = false
POLYGON / MULTIPOLYGON outer rings provide the point-count estimate
```

The artifact currently contains `POLYGON` lines only. Multipolygon semantics are
covered by Goal5303 and by the shared Goal5305 loader tests.

## Claim Boundary

Allowed summary:

```text
Goal5306 creates a bounded ArcGIS WaterBodies->BlockGroups WKT fixture and
metadata for the X-HD geo path. It is Level-B ingestion/conversion evidence
only.
```

Forbidden summaries:

```text
X-HD geo inputs are recovered.
WaterBodies/BlockGroups exact paper inputs are recovered.
Geo Figure 5 is reproduced.
The fixture proves geo correctness.
The fixture is representative of the paper's full US geo distribution.
Author/RTDL performance can now be compared.
```

## Validation

Commands run:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5306_water_bg_arcgis_bounded_fixture.py
py -m unittest tests.goal5306_xhd_water_bg_arcgis_bounded_fixture_test
```

Result:

```text
Ran 3 tests in 0.015s
OK
```

The Windows Python environment printed the known noisy prefix warning:

```text
Could not find platform independent libraries <prefix>
```

The tests passed.

## Next Recommended Goal

Goal5307 should run author `hd_exec` and RTDL on this same bounded fixture.
If author ingestion fails, fix the WKT contract before running RTDL.
