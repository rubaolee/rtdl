# Draft: WaterBodies/BG Exact-Equivalence Review Request

Status: `prepared_not_sent`

Suggested recipient:

```text
owner or external reviewer
```

Subject:

```text
X-HD WaterBodies/BG exact-equivalence decision request
```

Review question:

```text
Can the current deterministic public ArcGIS reconstruction be accepted as exact-equivalent for a renamed bounded public-reconstruction claim, or must it remain Level-B same-source evidence?
```

Evidence supporting possible acceptance:

```text
1. Both services are public ArcGIS sources matching the paper pair names.
2. WaterBodies and BlockGroups MBR deltas are under 1e-5 degrees.
3. Point-count deltas are small relative to paper logs: +6129 WaterBodies and +127 BlockGroups.
4. Author hd_exec with paper-config n_points_cell=8 reproduces the paper-log HDResult.
5. RTDL exact-witness route matches the author paper-config rerun within 2e-6.
6. Generated WKT sha256 values are recorded.
```

Evidence against exact self-promotion:

```text
1. No author-provided WKT file hashes are available.
2. No proof current ArcGIS services are the author's exact snapshot.
3. No byte-identical regeneration proof exists.
4. Point-count deltas are nonzero.
5. Statistics and scalar agreement do not prove byte identity.
```

Concrete public reconstruction identifiers:

```text
WaterBodies service item: 48c77cbde9a0470fb371f8c8a8a7421a
WaterBodies service URL: https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Detailed_Water_Bodies/FeatureServer
WaterBodies generated WKT sha256: 0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39
WaterBodies point-count delta: 6129
WaterBodies max_abs_mbr_delta: 2.9081737551450715e-06

BlockGroups service item: 2f5e592494d243b0aa5c253e75e792a4
BlockGroups service URL: https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_BlockGroups/FeatureServer
BlockGroups generated WKT sha256: 8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e
BlockGroups point-count delta: 127
BlockGroups max_abs_mbr_delta: 3.7103264247662082e-06
```

Allowed answers:

```text
1. exact_equivalent_accepted_with_renamed_bounded_public_reconstruction_claim
2. bounded_public_reconstruction_only_keep_level_b
3. not_accepted_keep_level_b
```

Default without explicit acceptance:

```text
bounded_public_reconstruction_only_keep_level_b
```

Claim boundary:

```text
This draft is not sent.
Exact-equivalence is not accepted unless a reviewer explicitly says so.
Point counts, MBRs, and HDResult alone are not treated as proof of exact paper input identity.
```
