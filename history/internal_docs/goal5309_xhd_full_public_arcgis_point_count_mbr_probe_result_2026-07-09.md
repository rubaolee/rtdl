# Goal5309 - X-HD Full-Public ArcGIS Point-Count / MBR Probe Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5309 runs the full-public ArcGIS point-count / MBR probe authorized by
Goal5308. It does not write full WKT, does not run author `hd_exec`, and does
not run RTDL. It only answers whether the public ArcGIS services are close
enough to the paper-log geo inputs to justify heavier Figure-5 work.

Short version:

```text
All four name-matched ArcGIS services were fully probed.
All four MBRs match the paper-log MBRs to < 1e-5 degrees.
ZCTA, WaterBodies, and BlockGroups point counts are very close to paper logs.
County point count is +3,039,134 points (+32.2%), so County-ZCTA is not exact.
WaterBodies-BlockGroups is a strong full-public candidate, but still not exact
without file/hash provenance.
```

## New / Updated Artifacts

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5309_full_public_arcgis_point_count_mbr_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_smoke_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_county_full_arcgis_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_zcta_full_arcgis_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_waterbodies_full_arcgis_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_blockgroups_full_arcgis_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
tests/goal5309_xhd_full_public_arcgis_probe_contract_test.py
tests/goal5309_xhd_full_public_arcgis_probe_result_test.py
```

The probe script now has:

```text
polygon outer-ring closure, but no line/point closure;
checkpoint resume from features_seen;
atomic checkpoint/output writes;
limited retry/backoff for ArcGIS 429/5xx/transient URL errors.
```

## Full-Public Probe Results

### County (`dtl_cnty.wkt`)

```text
service features = 3,144
geometry types = Polygon: 2,815; MultiPolygon: 329
paper point count = 9,438,045
observed author-loader point count = 12,477,179
delta = +3,039,134
relative delta = +32.200884823075115%
max abs MBR delta = 3.7104491212858193e-06
classification = extent_match_point_count_mismatch_not_exact
```

Interpretation:

```text
The public ArcGIS County service has the same national extent as the paper log,
but it is much more detailed by author-loader point count. This blocks exact
paper input status for the County-ZCTA pair.
```

### ZCTA (`uszipcode.wkt`)

```text
service features = 32,294
geometry types = Polygon: 30,709; MultiPolygon: 1,585
paper point count = 43,952,878
observed author-loader point count = 43,984,131
delta = +31,253
relative delta = +0.07110569642333773%
max abs MBR delta = 7.358398448786829e-06
classification = very_close_point_count_and_mbr_but_no_file_hash
```

Interpretation:

```text
The public ArcGIS ZCTA service is a strong full-public candidate by count and
MBR, but still lacks exact file/hash provenance.
```

### WaterBodies (`USADetailedWaterBodies.wkt`)

```text
service features = 463,591
geometry types = Polygon: 463,590; MultiPolygon: 1
paper point count = 22,818,694
observed author-loader point count = 22,824,823
delta = +6,129
relative delta = +0.02685955646716679%
max abs MBR delta = 2.9081737551450715e-06
classification = very_close_point_count_and_mbr_but_no_file_hash
```

Interpretation:

```text
The public ArcGIS WaterBodies service is a strong full-public candidate by
count and MBR, but still lacks exact file/hash provenance.
```

### BlockGroups (`USACensusBlockGroupBoundaries.wkt`)

```text
service features = 239,203
geometry types = Polygon: 236,966; MultiPolygon: 2,237
paper point count = 52,271,340
observed author-loader point count = 52,271,467
delta = +127
relative delta = +0.00024296296976507585%
max abs MBR delta = 3.7103264247662082e-06
classification = near_exact_point_count_and_mbr_but_no_file_hash
```

Interpretation:

```text
The public ArcGIS BlockGroups service is extremely close to the paper log by
point count and MBR, but still lacks exact file/hash provenance.
```

## Pair Decisions

### County -> ZCTA

```text
classification = full_public_candidate_but_not_exact_due_county_point_count_mismatch
```

Reason:

```text
County and ZCTA MBRs match paper logs, and ZCTA point count is very close, but
County has 3,039,134 more author-loader points than the paper log (+32.2%).
```

Allowed next:

```text
Investigate alternate County source/simplification before any Figure-5 geo
claim. Do not generate a full-public County-ZCTA WKT and call it exact.
```

### WaterBodies -> BlockGroups

```text
classification = strong_full_public_candidate_not_exact_without_file_hash
```

Reason:

```text
Both services match paper MBRs and point counts are extremely close:
WaterBodies +6,129 (+0.0269%), BlockGroups +127 (+0.000243%).
File/hash provenance is still absent.
```

Allowed next:

```text
After review accepts the full-public candidate boundary, generate full-public
WKT for this pair and run author/RTDL as a Level-B full-public candidate gate.
Do not call it exact paper input recovery unless file/hash provenance appears.
```

## Claim Boundary

Allowed summary:

```text
Goal5309 fully probes the four name-matched public ArcGIS geo services. It
finds strong full-public candidates for ZCTA, WaterBodies, and BlockGroups, but
County's point count is 32.2% above the paper log, so geo Figure-5 exact
reproduction remains blocked.
```

Forbidden summaries:

```text
X-HD Figure 5 geo is reproduced.
Exact paper WKT files are recovered.
Public ArcGIS services are proven byte-identical to the author's inputs.
County-ZCTA is ready for exact Figure-5 reproduction.
WaterBodies-BlockGroups is exact paper input.
Any author-vs-RTDL performance ratio is available from Goal5309.
Full paper reproduction is complete.
```

## Validation

Commands run:

```text
py -m unittest tests.goal5309_xhd_full_public_arcgis_probe_contract_test
py -m unittest tests.goal5309_xhd_full_public_arcgis_probe_contract_test tests.goal5309_xhd_full_public_arcgis_probe_result_test
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
```

Results:

```text
Ran 5 tests OK
Ran 9 tests OK
JSON validation OK
```

Long-running full-public probes completed locally:

```text
County:       3,144 features, 2 pages, 179.76s
ZCTA:         32,294 features, 57 pages, 597.26s, resumed from checkpoint
WaterBodies: 463,591 features, 464 pages, 640.52s
BlockGroups: 239,203 features, 120 pages, 929.21s
```
