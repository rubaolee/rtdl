# Draft: X-HD WaterBodies/BG Author Input Hash Request

Status: `prepared_not_sent`

Suggested recipients:

```text
X-HD authors / artifact owner
```

Subject:

```text
X-HD reproduction: WaterBodies/BG paper input hashes or regeneration provenance
```

Body:

```text
Hello,

We are reproducing the X-HD paper's WaterBodies -> BlockGroups case.
Our current public ArcGIS reconstruction is a strong Level-B candidate,
but we cannot claim exact paper reproduction without paper-run input
hashes, bytes, or byte-identical regeneration provenance.

Current evidence:

- Paper pair: USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
- Paper config: num_points_cell=8
- Author paper-config HDResult: 0.89643675088882446
- RTDL exact-witness HDResult (float64): 0.89643805666901011
- RTDL vs author abs diff: 1.3057801856453111e-06 <= 1.9999999999999999e-06
- WaterBodies public WKT sha256: 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
- BlockGroups public WKT sha256: 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
- WaterBodies point-count delta vs paper log: 6129
- BlockGroups point-count delta vs paper log: 127

Could you provide, or confirm availability of:

1. USADetailedWaterBodies.wkt bytes or sha256 from the paper-run HDDatasets tree.
2. USACensusBlockGroupBoundaries.wkt bytes or sha256 from the paper-run HDDatasets tree.
3. If files cannot be shared, exact source URLs, snapshot dates, export parameters, and conversion scripts sufficient to regenerate the paper-run WKT files.
4. The exact command line or config for the paper-log run confirming num_points_cell=8 for this pair.
5. Any preprocessing, simplification, precision, coordinate, or ring/vertex extraction policy used to produce the paper-run WKT inputs.

If the files cannot be shared, hashes plus exact source snapshots,
export parameters, and conversion details would still let us classify
the reproduction boundary accurately without overclaiming exact paper
reproduction.

Thank you.
```

Claim boundary:

```text
This draft is not sent.
No external artifacts are claimed acquired.
No exact paper dataset claim is made.
```
