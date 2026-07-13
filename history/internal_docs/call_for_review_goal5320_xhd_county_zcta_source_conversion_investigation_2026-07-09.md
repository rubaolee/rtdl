# Call For Review: Goal5320 X-HD County-ZCTA Source / Conversion Investigation

Please strictly review Goal5320.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5320_county_zcta_source_conversion_investigation.json
tests/goal5320_xhd_county_zcta_source_conversion_investigation_test.py
history/internal_docs/goal5320_xhd_county_zcta_source_conversion_investigation_result_2026-07-09.md
```

Supporting prior artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5302_census_tiger_source_resolution_plan_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
```

## Context

Goal5317 ranked County-ZCTA as a lower-priority exact-input target because the
full-public ArcGIS County candidate has paper-like MBRs but a large point-count
mismatch.

Goal5320 investigates whether any already-identified County source or conversion
rule is close enough to justify execution:

```text
paper dtl_cnty.wkt point count = 9,438,045
```

## Goal5320 Summary

The result classifies three County candidates:

```text
current ArcGIS USA_Census_Counties service:
  12,477,179 points
  +3,039,134 (+32.2%)
  not exact, too many points

direct Census TIGER2023 COUNTY zip, all records:
  8,201,082 points
  -1,236,963 (-13.1%)
  not exact, too few points and includes territories

direct Census TIGER2023 COUNTY zip, 50 states + DC:
  8,081,061 points
  -1,356,984 (-14.4%)
  not exact, same feature count as ArcGIS but too few points

prior RayJoin dtl_cnty_Point.cdb:
  17,325,792 points
  related topology artifact, not X-HD WKT provenance
```

ZCTA context:

```text
paper uszipcode.wkt point count = 43,952,878
ArcGIS current ZIP point count  = 43,984,131
delta                           = +31,253 (+0.0711%)
```

Exit label:

```text
county_zcta_exact_provenance_not_found__source_conversion_blocked
```

## Review Questions

1. Does the evidence support the conclusion that current ArcGIS County is not an
   exact paper input because its point count is +32.2% from the paper log?
2. Does the direct TIGER2023 County parse provide useful evidence that official
   TIGER2023 is also not the missing author `dtl_cnty.wkt`?
3. Is the 50 states + DC TIGER filter a reasonable diagnostic, and does it
   strengthen the conclusion that source/conversion identity is unresolved?
4. Is it correct to classify the prior RayJoin `dtl_cnty_Point.cdb` as related
   but not X-HD WKT provenance?
5. Does the ZCTA evidence support treating County as the primary blocker?
6. Does Goal5320 correctly avoid claiming exact input recovery, Figure-5
   reproduction, or a performance ratio?
7. Should the next County-ZCTA work remain source/provenance search rather than
   author/RTDL route execution?
8. Is the requested exit label acceptable?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5320_county_zcta_source_conversion_blocked
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5320

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
8. ...
```
