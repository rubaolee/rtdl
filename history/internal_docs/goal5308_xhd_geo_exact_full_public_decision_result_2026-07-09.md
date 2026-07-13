# Goal5308 - X-HD Geo Exact / Full-Public Decision Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5308 decides what the X-HD geo line is allowed to claim after Goals5302-5307.

Short version:

```text
Both Figure-5 WKT pair names have bounded author/RTDL scalar matches.
Exact paper WKT files are still unavailable.
Therefore Figure-5 reproduction is still not claimed.
The next valid step is a full-public point-count / MBR / author-loader probe,
not a performance-ratio run.
```

## New Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5308_geo_exact_full_public_decision_2026-07-09.json
tests/goal5308_xhd_geo_exact_full_public_decision_test.py
```

## Exact File Availability

Known author log root:

```text
/local/storage/shared/HDDatasets/geo
```

Known exact paths from author logs:

```text
/local/storage/shared/HDDatasets/geo/dtl_cnty.wkt
/local/storage/shared/HDDatasets/geo/uszipcode.wkt
/local/storage/shared/HDDatasets/geo/USADetailedWaterBodies.wkt
/local/storage/shared/HDDatasets/geo/USACensusBlockGroupBoundaries.wkt
```

Current evidence:

```text
local generated exact files = false
current POD exact paths found = false
known author paths available on current POD = false
```

This agrees with earlier Goal5214 / Goal5295 availability work: paths are known
from author logs, but files are unavailable.

## Paper-Log Geo Targets

Paper-log records show the real geo workloads are far larger than the bounded
fixtures:

### County -> ZCTA

```text
paper log file = dtl_cnty.wkt_uszipcode.wkt.json
paper log HDResult = 0.4093780517578125
paper log point counts = 9,438,045 / 43,952,878
paper log path input1 = /local/storage/shared/HDDatasets/geo/dtl_cnty.wkt
paper log path input2 = /local/storage/shared/HDDatasets/geo/uszipcode.wkt
```

Bounded evidence from Goals5303-5305:

```text
bounded point counts = 38,034 / 50,272
author HDResult = 65.44752502441406
RTDL HDResult = 65.44751976280666
matched = true
```

### WaterBodies -> BlockGroups

```text
paper log file = USADetailedWaterBodies.wkt_USACensusBlockGroupBoundaries.wkt.json
paper log HDResult = 0.8964367508888245
paper log point counts = 22,818,694 / 52,271,340
paper log path input1 = /local/storage/shared/HDDatasets/geo/USADetailedWaterBodies.wkt
paper log path input2 = /local/storage/shared/HDDatasets/geo/USACensusBlockGroupBoundaries.wkt
```

Bounded evidence from Goals5306-5307:

```text
bounded point counts = 124 / 894
author HDResult = 72.38665008544922
RTDL HDResult = 72.38664516014835
matched = true
```

## Decision

```text
level_b_bounded_geo_packet_ready_for_review = true
level_c_exact_paper_geo_reproduction_blocked = true
next_allowed_goal = full_public_arcgis_point_count_mbr_probe_before_any_figure5_claim
```

Reason:

```text
A full-public reconstruction must first show point counts, MBRs, and
author-loader point-stream semantics close to the paper logs. Bounded
first-OBJECTID fixtures are too small and non-representative.
```

## Authorized Next Goal

The next implementation goal should be a full-public probe, not a performance
run:

```text
Goal5309_full_public_arcgis_geo_point_count_mbr_probe
```

Minimum scope:

1. Stream/page ArcGIS name-matched services without constructing full WKT first.
2. Compute author-loader point counts and MBRs for:
   - full County;
   - full ZCTA;
   - full WaterBodies;
   - full BlockGroups.
3. Compare those counts/MBRs with paper-log counts/MBRs.
4. Classify each pair:
   - exact-like candidate;
   - public-reconstruction candidate;
   - mismatch / do not use for Figure-5 claim.

Only after that probe may we decide whether to generate full-public WKT and run
author/RTDL on it.

## Claim Boundary

Allowed summary:

```text
Goals5302-5307 complete bounded Level-B scalar correctness for both X-HD
Figure-5 WKT pair names. Goal5308 blocks exact/Figure-5 claims until
full-public or exact input provenance is stronger.
```

Forbidden summaries:

```text
X-HD Figure 5 is reproduced.
Exact geo WKT inputs are recovered.
Bounded first-OBJECTID fixtures are representative.
Performance ratio is available.
Full paper reproduction is complete.
```

## Validation

Command run:

```text
py -m unittest tests.goal5308_xhd_geo_exact_full_public_decision_test
```

Result:

```text
Ran 3 tests OK
```
