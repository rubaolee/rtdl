# Goal5318 - X-HD WaterBodies/BG Exact-Provenance Search Result

## Verdict

```text
completed_water_bg_exact_provenance_not_found_keep_level_b
```

Goal5318 searched whether the current full-public
`USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt` candidate can
be promoted from Level-B same-source evidence to exact paper-input provenance.
It cannot be promoted yet.

The result artifact is:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
```

## What Was Searched

This goal did not run new author or RTDL performance code. It searched existing
provenance evidence and public metadata:

- Goal5310 full-public WKT manifest and generated WKT hashes.
- Goal5313/Goal5314 author paper-config and RTDL witness evidence.
- Goal5317 exact-input acquisition gap matrix.
- ArcGIS FeatureServer service/layer metadata for:
  - `USA_Detailed_Water_Bodies`;
  - `USA_Census_BlockGroups`.
- ArcGIS item metadata for both FeatureServer items.
- The linked WaterBodies layer package item referenced by ArcGIS metadata.
- Repository search for author WKT hashes, `/local/storage/shared/HDDatasets`
  residue, and prior RayJoin CDB assets.

## Strong Evidence Preserved

WaterBodies/BG remains the strongest current geo Level-B candidate.

Local full-public WKT candidate:

```text
WaterBodies:
  WKT sha256 = 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
  observed author-loader points = 22,824,823
  paper points = 22,818,694
  delta = +6,129 (+0.0269%)

BlockGroups:
  WKT sha256 = 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
  observed author-loader points = 52,271,467
  paper points = 52,271,340
  delta = +127 (+0.000243%)
```

Paper-config value evidence:

```text
author hd_exec n_points_cell=8 = 0.8964367508888245
paper-log HDResult             = 0.8964367508888245
RTDL exact-witness float64     = 0.8964380566690101
same witness float32           = 0.8964367508888245
declared tolerance             = 2e-6
```

ArcGIS metadata supports same-source discussion:

- WaterBodies service/item identify `USA Detailed Water Bodies`, USGS National
  Hydrography Dataset lineage, public ArcGIS service item
  `48c77cbde9a0470fb371f8c8a8a7421a`, and a linked layer package item.
- BlockGroups service/item identify 2020 U.S. Census block group boundaries,
  Census/TIGER lineage, public ArcGIS service item
  `2f5e592494d243b0aa5c253e75e792a4`, and update/vintage metadata.

## Why This Is Still Not Exact

The exact dataset rule from Goal5317 requires one of:

```text
author-provided input files or archives
author-provided hashes for converted point files
byte-identical regenerated point files from a documented author conversion pipeline
external review accepting deterministic public-source regeneration as equivalent
```

Goal5318 found none of these.

Negative findings:

```text
author USADetailedWaterBodies.wkt file found = false
author USACensusBlockGroupBoundaries.wkt file found = false
author WaterBodies WKT sha256 found = false
author BlockGroups WKT sha256 found = false
byte-identical regeneration proven = false
ArcGIS current snapshot exact-equivalence proven = false
external review accepting public snapshot as exact = false
```

The public ArcGIS metadata is useful, but insufficient:

- Current WKT point counts still differ from the paper logs.
- ArcGIS item/layer metadata gives source family and update/vintage hints, not
  author WKT bytes.
- The BlockGroups service is updated data, not a frozen author snapshot.
- Matching MBR/count/value evidence is not a file/hash proof.

Prior RayJoin CDB assets are related but not usable as X-HD WKT provenance.
They are CDB/topology artifacts with different denominators, not the author's
`/local/storage/shared/HDDatasets/geo/*.wkt` files.

## Decision

```text
exit_label = water_bg_exact_provenance_not_found_keep_level_b
```

Allowed summary:

```text
WaterBodies/BG remains the strongest current geo Level-B candidate: public
ArcGIS WKT candidate has near-paper counts/MBRs, author paper-config
n_points_cell=8 reproduces paper-log HDResult, and RTDL witness agrees within
the declared float64-vs-author-float32 tolerance. Exact input provenance is
still not proven because author WKT files/hashes or accepted deterministic
regeneration proof are missing.
```

Forbidden summaries:

```text
WaterBodies/BG exact paper WKT files were recovered.
Current ArcGIS public services are proven byte-identical to author HDDatasets WKT inputs.
Figure 5 geo is reproduced.
Author-vs-RTDL performance ratio is authorized.
Matching HDResult/counts/MBRs proves exact dataset identity.
```

## Validation

Commands run:

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5318_water_bg_exact_provenance_search.json
py -m unittest tests.goal5318_xhd_water_bg_exact_provenance_search_test
```

Result:

```text
Ran 6 tests OK
```

The local Python launcher also printed the known noisy environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

Do not run more WaterBodies/BG performance work by default.

Next productive routes are:

1. Seek external author WKT files/hashes or archived export packages.
2. Ask for external review on whether current ArcGIS public-source
   reconstruction can ever be accepted as exact-equivalent despite small point
   deltas.
3. If exact provenance cannot be obtained, keep WaterBodies/BG as Level-B and
   move to another exact-input target.

POD is not needed unless a concrete file/provenance lead requires remote
verification.
