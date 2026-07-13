# Goal5310 - X-HD WaterBodies -> BlockGroups Full-Public WKT Candidate Result

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

Goal5310 materializes the strongest Goal5309 geo candidate into full-public
WKT files:

```text
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
```

This is **not** exact paper dataset recovery. It is a full-public ArcGIS
candidate generated from name-matched services whose point counts / MBRs were
shown by Goal5309 to be very close to the paper logs.

## New / Updated Artifacts

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5310_water_bg_full_public_wkt_candidate.py
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/USADetailedWaterBodies.wkt.full_public_arcgis_candidate.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/USACensusBlockGroupBoundaries.wkt.full_public_arcgis_candidate.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/manifest.json
Paper-reproduction-apps/x-hd-paper/results/goal5310_water_bg_full_public_wkt_checkpoints/waterbodies.json
Paper-reproduction-apps/x-hd-paper/results/goal5310_water_bg_full_public_wkt_checkpoints/blockgroups.json
tests/goal5310_xhd_water_bg_full_public_wkt_candidate_test.py
```

## Materialization Result

### WaterBodies

```text
features = 463,591
pages = 464
geometry types = Polygon: 463,590; MultiPolygon: 1
author-loader point count = 22,824,823
paper-log point count = 22,818,694
delta = +6,129 (+0.0268596%)
MBR max abs delta ~= 2.91e-6 degrees
WKT bytes = 741,925,630
sha256 = 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
```

### BlockGroups

```text
features = 239,203
pages = 120
geometry types = Polygon: 236,966; MultiPolygon: 2,237
author-loader point count = 52,271,467
paper-log point count = 52,271,340
delta = +127 (+0.000242963%)
MBR max abs delta ~= 3.71e-6 degrees
WKT bytes = 1,560,257,609
sha256 = 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
```

## Implementation Notes

The generator is app-owned and deliberately conservative:

```text
uses Goal5309 service definitions and retry/query logic;
streams pages and appends WKT line by line;
records checkpoints after each page;
fails closed if checkpoint exists but output WKT is missing;
records sha256 only after service completion;
keeps exact/Figure-5/performance claims false.
```

The generated WKT uses the same one-geometry-per-line convention as the
bounded fixtures. Polygon rings are closed for WKT; author-loader point counts
remain based on polygon outer rings, matching the Goal5309 probe contract.

## What This Enables

Goal5310 makes the next gate concrete:

```text
Goal5311: upload or regenerate these full-public WKT files on POD, run author
hd_exec, and record the author HDResult / point counts / process status.
```

If author ingestion succeeds, a later gate can run RTDL on the same full-public
candidate.

## Claim Boundary

Allowed summary:

```text
Goal5310 materializes the WaterBodies-BlockGroups full-public ArcGIS candidate
into author-readable WKT and records complete file hashes, sizes, point counts,
and MBRs. It is ready for an author ingestion gate.
```

Forbidden summaries:

```text
Exact paper WKT files are recovered.
WaterBodies-BlockGroups Figure 5 is reproduced.
Author/RTDL correctness is proven.
Author-vs-RTDL performance ratio is available.
The public ArcGIS WKT files are byte-identical to the author's files.
Full X-HD paper reproduction is complete.
```

## Validation

Commands run:

```text
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5310_water_bg_full_public_wkt_candidate.py
py -m unittest tests.goal5310_xhd_water_bg_full_public_wkt_candidate_test
py -m json.tool Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/manifest.json
```

Results:

```text
py_compile OK
Ran 6 tests OK
JSON validation OK
```

Generation run:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5310_water_bg_full_public_wkt_candidate.py \
  --output-dir Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate \
  --checkpoint-dir Paper-reproduction-apps/x-hd-paper/results/goal5310_water_bg_full_public_wkt_checkpoints \
  --manifest Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/manifest.json \
  --page-size 2000 \
  --timeout 120
```

Result:

```text
status = water_bg_full_public_wkt_candidate_complete
elapsed_sec = 1,259.575
```
