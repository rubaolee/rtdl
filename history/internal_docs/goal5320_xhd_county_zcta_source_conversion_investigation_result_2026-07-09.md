# Goal5320 - X-HD County-ZCTA Source / Conversion Investigation

Date: 2026-07-09

Status: `implemented_review_pending`

## Purpose

Goal5320 investigates the remaining blocker for the X-HD Figure-5
`dtl_cnty.wkt -> uszipcode.wkt` row after Goal5317 ranked it as a lower-priority
exact-input target.

The question is deliberately narrow:

```text
Is there an already-identified public County source or conversion rule close
enough to the paper-log point count to justify full-public author/RTDL route
execution?
```

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5320_county_zcta_source_conversion_investigation.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5320.county_zcta_source_conversion_investigation.v1
```

## Inputs Checked

Existing project evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5302_census_tiger_source_resolution_plan_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
src/rtdsl/datasets.py
history/internal_docs/docs_reports/goal4374_cleanup_bigtest_2026-06-14/rayjoin_author_call_for_review_2026-06-14.md
```

External / live metadata:

```text
https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer/0?f=pjson
https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_ZIP_Code_Areas_anaylsis/FeatureServer/0?f=pjson
https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip
```

## Key Findings

### 1. Current ArcGIS County Is Too Detailed

The current ArcGIS `USA_Census_Counties` service has the right feature count and
paper-like MBR, but not the paper point count:

```text
paper dtl_cnty point count        = 9,438,045
ArcGIS current County point count = 12,477,179
delta                             = +3,039,134 (+32.2%)
```

The live layer metadata says the layer is 2020 Census County boundaries sourced
from Census 2020 TIGER FGDB National Sub-State and edited with TIGER Hydrography
to add a detailed coastline. The metadata also says it is updated annually.
That makes it a plausible same-source family, but not an exact paper input.

### 2. Direct Census TIGER2023 County Is Too Small

Goal5320 downloaded the official national TIGER2023 County ZIP and parsed the
`.shp` directly. Its archive hash is recorded in the artifact:

```text
tl_2023_us_county.zip sha256 =
692e12c30c83adcaabdbac0d3954fafa55e1c89a24b36d95e72e02dff938652e
```

Raw all-record parse:

```text
records = 3,235
points  = 8,201,082
delta   = -1,236,963 (-13.1%)
```

50 states + DC filter:

```text
records = 3,144
points  = 8,081,061
delta   = -1,356,984 (-14.4%)
```

So the direct official TIGER2023 County shapefile is not the missing author
`dtl_cnty.wkt` either.

### 3. Prior RayJoin CDB Is Related But Not X-HD WKT Provenance

The old RayJoin County CDB evidence records:

```text
dtl_cnty_Point.cdb points = 17,325,792
```

That is a CDB/topology artifact with a different denominator, and it is far from
the X-HD paper-log WKT point count. It cannot be used as X-HD exact WKT
provenance.

### 4. ZCTA Is Not The Primary Blocker

The current ArcGIS ZCTA/ZIP service is much closer to the paper count:

```text
paper uszipcode point count = 43,952,878
ArcGIS ZIP point count      = 43,984,131
delta                       = +31,253 (+0.0711%)
```

This still lacks file/hash provenance, but compared with the County mismatch it
is not the first blocker.

## Exit Label

```text
county_zcta_exact_provenance_not_found__source_conversion_blocked
```

## Interpretation

The current blocker is:

```text
County source or conversion rule, not RTDL route execution.
```

Possible but unproven hypotheses:

```text
author used an older Esri/TIGER vintage between direct TIGER2023 and current
ArcGIS detailed-coastline point counts;

author used a specific ArcGIS export or simplification tolerance not captured
by current service metadata;

author used a WKT conversion / coordinate precision rule that drops or merges
some current ArcGIS vertices;

author used a private HDDatasets snapshot.
```

## Validation

Commands:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5320_county_zcta_source_conversion_investigation.json
py -m unittest tests.goal5320_xhd_county_zcta_source_conversion_investigation_test
```

Observed:

```text
Ran 6 tests in 0.001s
OK
```

The local launcher printed:

```text
Could not find platform independent libraries <prefix>
```

This is known Windows environment noise and did not affect test success.

## Claim Boundary

Allowed:

```text
Goal5320 shows that the already-identified County public candidates do not
recover the X-HD paper dtl_cnty point count, and that County-ZCTA remains
source/conversion blocked.
```

Forbidden:

```text
County-ZCTA exact paper input recovery;
current ArcGIS County service is exact author input;
direct TIGER2023 County is exact author input;
old RayJoin CDB is X-HD WKT provenance;
full-public County-ZCTA Figure-5 evidence;
author-vs-RTDL performance ratio.
```

## POD Use

Goal5320 did not use POD.

POD is not expected for ordinary County-ZCTA source investigation. Use POD only
if a concrete new source/conversion candidate appears and needs author `hd_exec`
or RTDL verification.
