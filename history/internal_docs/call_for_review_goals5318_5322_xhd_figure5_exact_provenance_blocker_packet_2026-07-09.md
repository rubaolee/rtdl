# Call For Review: Goals5318-5322 X-HD Figure-5 Exact-Provenance Blocker Packet

Please strictly review Goals5318-5322 as one X-HD Figure-5 exact-input
provenance packet.

## Files To Review

Goal5318 WaterBodies/BlockGroups exact-provenance search:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
tests/goal5318_xhd_water_bg_exact_provenance_search_test.py
history/internal_docs/goal5318_xhd_water_bg_exact_provenance_search_result_2026-07-09.md
history/internal_docs/call_for_review_goal5318_xhd_water_bg_exact_provenance_search_2026-07-09.md
```

Goal5319 graphics exact-provenance search:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
tests/goal5319_xhd_graphics_exact_provenance_search_test.py
history/internal_docs/goal5319_xhd_graphics_exact_provenance_search_result_2026-07-09.md
history/internal_docs/call_for_review_goal5319_xhd_graphics_exact_provenance_search_2026-07-09.md
```

Goal5320 County/ZCTA source-conversion investigation:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5320_county_zcta_source_conversion_investigation.json
tests/goal5320_xhd_county_zcta_source_conversion_investigation_test.py
history/internal_docs/goal5320_xhd_county_zcta_source_conversion_investigation_result_2026-07-09.md
history/internal_docs/call_for_review_goal5320_xhd_county_zcta_source_conversion_investigation_2026-07-09.md
```

Goal5321 OSM Lakes/Parks/AllNodes provenance search:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
tests/goal5321_xhd_osm_lakes_parks_allnodes_provenance_test.py
history/internal_docs/goal5321_xhd_osm_lakes_parks_allnodes_provenance_result_2026-07-09.md
history/internal_docs/call_for_review_goal5321_xhd_osm_lakes_parks_allnodes_provenance_2026-07-09.md
```

Goal5322 BraTS2020 access/conversion provenance:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5322_brats2020_access_conversion_provenance.json
tests/goal5322_xhd_brats2020_access_conversion_provenance_test.py
history/internal_docs/goal5322_xhd_brats2020_access_conversion_provenance_result_2026-07-09.md
history/internal_docs/call_for_review_goal5322_xhd_brats2020_access_conversion_provenance_2026-07-09.md
```

Supporting matrix:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
tests/goal5317_xhd_figure5_exact_input_gap_matrix_test.py
history/internal_docs/goal5317_xhd_figure5_exact_input_acquisition_gap_matrix_result_2026-07-09.md
```

## Packet Summary

Goal5317 states the rule:

```text
Level-C exact status requires author files/hashes, byte-identical regeneration,
or externally accepted deterministic public-source equivalence.
Matching point counts, MBRs, statistics, path names, HDResult, or author rerun
is not enough.
```

Goals5318-5322 apply that rule to all current Figure-5 exact-input families.

## Per-Goal Status

### Goal5318 - WaterBodies/BG

Exit:

```text
water_bg_exact_provenance_not_found_keep_level_b
```

Preserved Level-B evidence:

```text
WaterBodies point delta = +6,129 (+0.0269%)
BlockGroups point delta = +127 (+0.000243%)
author paper-config n_points_cell=8 reproduces paper-log HDResult exactly
RTDL exact-witness float64 matches author/paper float32 within 2e-6
```

Still missing:

```text
author WKT files/hashes;
byte-identical regeneration proof;
external acceptance of current ArcGIS services as exact-equivalent.
```

### Goal5319 - Graphics

Exit:

```text
graphics_exact_provenance_not_found_keep_level_b
```

Preserved Level-B evidence:

```text
Dragon -> HappyBuddha value-matched;
ThaiStatuette-scaled -> HappyBuddha value-matched;
ThaiStatuette-scaled -> AsianDragon-scaled value-matched;
Dragon -> AsianDragon-scaled remains an author-value no-go.
```

Still missing:

```text
author graphics files/hashes;
byte-identical public Stanford regeneration proof;
author preprocessing/scaling proof.
```

### Goal5320 - County/ZCTA

Exit:

```text
county_zcta_exact_provenance_not_found__source_conversion_blocked
```

Key finding:

```text
paper dtl_cnty.wkt point count = 9,438,045
current ArcGIS County = 12,477,179 (+32.2%)
direct TIGER2023 County all records = 8,201,082 (-13.1%)
direct TIGER2023 County 50 states + DC = 8,081,061 (-14.4%)
```

Interpretation:

```text
County source/conversion identity is blocked. Do not run full-public
County-ZCTA as Figure-5 evidence under the current source mapping.
```

### Goal5321 - OSM Lakes/Parks/AllNodes

Exit:

```text
osm_lakes_parks_allnodes_exact_provenance_not_found__snapshot_filter_blocked
```

Author log evidence:

```text
lakes.bz2.wkt -> parks.bz2.wkt
HDResult = 55.734275817871094
point counts = 301,704,289 / 403,688,408
```

Public catalog evidence exists, but exact identity is blocked by:

```text
missing author files/hashes;
missing OSM planet snapshot date/hash;
missing extraction filters;
missing WKT conversion rules.
```

### Goal5322 - BraTS2020

Exit:

```text
brats2020_exact_provenance_not_found__access_and_conversion_blocked
```

Author log evidence:

```text
BraTS2020_ValidationData
500 unique pairs / 2500 records
point count range = 887,826 .. 1,964,247
representative pair =
  BraTS20_Validation_001_flair.nii -> BraTS20_Validation_033_flair.nii
  HDResult = 26.645824432373047
```

Official-source finding:

```text
BraTS2020 data access requires CBICA IPP / BraTS'20 Data Request;
validation data are NIfTI MRI volumes, not X-HD-ready point sets.
```

Still missing:

```text
authorized validation NIfTI files;
file hashes;
author image list / order;
NIfTI-to-point conversion rule;
converted point-set hashes.
```

## Packet-Level Claim Boundary

Allowed:

```text
Goals5318-5322 classify all current X-HD Figure-5 exact-input families.
Several rows have strong Level-B evidence, but none is proven Level-C exact
paper input reproduction under the project rule.
```

Forbidden:

```text
full X-HD paper reproduction;
Figure 5 reproduction complete;
exact paper dataset recovery;
author-vs-RTDL performance ratio;
using counts/MBRs/statistics/path names/HDResult as exact input proof;
running more performance work before a new provenance lead appears.
```

## Review Questions

1. Is the Goal5317 exact-input rule correctly applied across Goals5318-5322?
2. Does WaterBodies/BG remain strong Level-B but not exact?
3. Does graphics remain Level-B despite value-matched public candidates?
4. Is County/ZCTA correctly classified as source/conversion blocked?
5. Is OSM correctly classified as snapshot/filter/conversion blocked?
6. Is BraTS correctly classified as access/conversion blocked?
7. Are POD expectations correct: no POD until concrete files/snapshots/data or
   conversion artifacts exist?
8. Are the forbidden claims complete?
9. Should the next project step be external data/provenance acquisition or
   reviewer decision, rather than new route/performance code?
10. Are any rows strong enough for an externally accepted Level-C exact claim,
    or should all remain Level-B / blocked as written?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5322_exact_provenance_blocker_packet
or
Verdict: approve_with_required_amendments
or
Verdict: block_packet

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
10. ...
```
