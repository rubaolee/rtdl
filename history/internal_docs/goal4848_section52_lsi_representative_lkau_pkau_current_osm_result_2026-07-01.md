# Goal4848 Result: One Representative Section 5.2 LSI Lakes/Parks Route

Date: 2026-07-01

## Decision Boundary

The original Goal4848 "finish all six remaining Lakes/Parks pairs" was stopped by user instruction.
The authorized replacement scope is:

> Rationally find one usable representative pair, finish that route, and stop.

This report therefore does **not** claim all six remaining Section 5.2 Lakes/Parks pairs are reproduced.

## Representative Chosen

Representative pair:

- Lakes: current Geofabrik Australia OSM water polygons
- Parks: current Geofabrik Australia OSM park/national-park polygons
- Label: `current_osm_geofabrik_representative_cdb`

Why this route:

- Exact SpatialHadoop/RayJoin Lakes/Parks CDB inputs were not available in the current workspace/POD cache.
- The old Google Drive/S3 links found in prior and current audits are unavailable.
- Geofabrik provides a current public Australia OSM extract, which is a reasonable representative route after the user explicitly authorized one usable representative instead of all six exact pairs.

This is **not** an exact paper CDB and not a same-snapshot SpatialHadoop input.

## Input Construction

POD work directory:

```text
/workspace/goal4848_rep/current_osm_au
```

Source:

```text
https://download.geofabrik.de/australia-oceania/australia-latest.osm.pbf
```

OSM extraction commands:

```bash
osmium tags-filter -O -o lakes.filtered.osm.pbf australia-latest.osm.pbf \
  w/natural=water r/natural=water

osmium tags-filter -O -o parks.filtered.osm.pbf australia-latest.osm.pbf \
  w/leisure=park r/leisure=park w/boundary=national_park r/boundary=national_park

osmium export -O --geometry-types=polygon -f geojsonseq -o lakes.geojsonseq lakes.filtered.osm.pbf
osmium export -O --geometry-types=polygon -f geojsonseq -o parks.geojsonseq parks.filtered.osm.pbf
```

CDB conversion utility:

```text
history/internal_docs/goal4848_geojsonseq_to_cdb.py
```

CDB summaries:

| Input | features | chains | points | artifact |
| --- | ---: | ---: | ---: | --- |
| lakes | 316,399 | 357,910 | 14,788,065 | `history/internal_docs/goal4848_representative_artifacts/lakes_cdb_summary.json` |
| parks | 50,090 | 51,130 | 992,505 | `history/internal_docs/goal4848_representative_artifacts/parks_cdb_summary.json` |

Claim boundary of generated CDBs:

- LSI ring geometry only.
- No overlay topology claim.
- No PIP claim.
- No full Section 5.7 claim.

## AuthorPatch Baseline

Author binary:

```text
/workspace/RayJoin_goal4840_author_probe/release_probe/bin/query_exec
```

Forward command:

```bash
query_exec \
  -poly1 lakes_Australia_current_osm_Point.cdb \
  -poly2 parks_Australia_current_osm_Point.cdb \
  -serialize=/workspace/goal4848_rep/current_osm_au/serialize_lsi_current_au \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -query=lsi \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false
```

Forward result:

```text
Intersections: 13622
Read map 0: 134851 ms
Read map 1: 13040.8 ms
Load Data: 38.9812 ms
Adaptive Grouping: 12.325 ms
Build Index: 12.9468 ms
Warmup: 6.48999 ms
Query: 1.26543 ms
Cleanup: 26.7529 ms
```

Reverse command used the same flags with `parks` as `-poly1` and `lakes` as `-poly2`.

Reverse result:

```text
Intersections: 13452
Read map 0: 9673.56 ms
Read map 1: 133713 ms
Load Data: 39.7241 ms
Adaptive Grouping: 0.972986 ms
Build Index: 1.58 ms
Warmup: 20.8669 ms
Query: 4.16341 ms
Cleanup: 108.203 ms
```

## Direction Contract Learned

For `query_exec -query=lsi`, the effective query side is `poly2` over the `poly1` base.

Therefore, to compare RTDL's bundled RayJoin helper to:

```text
AuthorPatch: -poly1 lakes -poly2 parks
```

the matching RTDL helper call is:

```text
left = parks
right = lakes
```

The opposite RTDL order matches the author's reverse command.

## RTDL Routes Tested

### Wrong Route: Generic RTDL Segment Kernel

Script:

```text
history/internal_docs/goal4848_rtdl_lsi_count.py
```

Artifact:

```text
history/internal_docs/goal4848_representative_artifacts/rtdl_lsi_current_au_optix_summary.json
```

Result:

```json
{
  "left_segment_count": 14430155,
  "right_segment_count": 941375,
  "load_sec": 117.45794809609652,
  "run_sec": 16.76136377453804,
  "result": {
    "row_count": 103794,
    "sha256": "a1ca46fd0bcd874eff07389e9a9462a29b38ad97f73d046ad836a4dcc8422649"
  }
}
```

Conclusion:

- This is **not** equivalent to RayJoin Section 5.2 LSI.
- It counts generic emitted segment-pair intersections differently from the paper route.
- It must not be used for a paper-reproduction performance claim.

### Correct Route: v2.14 Bundled RayJoin LSI Helper

Script:

```text
history/internal_docs/goal4848_rtdl_rayjoin_lsi_helper_count.py
```

Claim boundary:

- Uses released v2.14 bundled RayJoin helper path.
- Section 5.2 LSI count/hash only.
- Not a generic-language proof.
- Not overlay/PIP/full Section 5.7.

Forward RTDL helper order:

```text
left = lakes
right = parks
```

Artifact:

```text
history/internal_docs/goal4848_representative_artifacts/rtdl_rayjoin_lsi_helper_current_au_optix_summary.json
```

Result:

```json
{
  "left_segment_count": 14430155,
  "right_segment_count": 941375,
  "load_sec": 21.125477254390717,
  "run_sec": 2.8358296900987625,
  "native_timings": {
    "emitted_count": 13452,
    "hot_call_sec": 2.8357882872223854,
    "mode": "count_prepared_left_grouped_range_direct_intersection"
  },
  "result": {
    "row_count": 13452,
    "sha256": "83071b242c1813c78ceeb135b5ba7ccd946817cbf3463fbd0061ecc03c96b98c"
  }
}
```

This matches AuthorPatch reverse command count: `13452`.

Reverse RTDL helper order:

```text
left = parks
right = lakes
```

Artifact:

```text
history/internal_docs/goal4848_representative_artifacts/rtdl_rayjoin_lsi_helper_current_au_optix_reverse_summary.json
```

Result:

```json
{
  "left_segment_count": 941375,
  "right_segment_count": 14430155,
  "load_sec": 20.97937474399805,
  "run_sec": 5.428064227104187,
  "native_timings": {
    "emitted_count": 13622,
    "hot_call_sec": 5.428013116121292,
    "mode": "count_prepared_left_grouped_range_direct_intersection"
  },
  "result": {
    "row_count": 13622,
    "sha256": "969a711f415a635b12c4f6f54823fdfe6fabe9ce7c250024dc0e30420e5601a7"
  }
}
```

This matches AuthorPatch forward command count: `13622`.

## Result Summary

| Route | Effective query direction | Count | Match |
| --- | --- | ---: | --- |
| AuthorPatch forward: lakes base, parks query | parks over lakes | 13,622 | baseline |
| RTDL helper reverse: left parks, right lakes | parks over lakes | 13,622 | yes |
| AuthorPatch reverse: parks base, lakes query | lakes over parks | 13,452 | baseline |
| RTDL helper forward: left lakes, right parks | lakes over parks | 13,452 | yes |
| Generic RTDL segment kernel: lakes left, parks right | generic segment rows | 103,794 | no, wrong semantics |

## Performance Interpretation

Allowed statement:

- On this current-OSM Australia representative, the v2.14 bundled RayJoin LSI helper reproduces AuthorPatch LSI counts when the query direction is aligned.

Bounded timing observations:

- AuthorPatch forward hot query: `1.26543 ms`.
- RTDL helper matching direction `run_sec`: `5.428064 s`.
- AuthorPatch process time is dominated by CDB reading (`~147.9 s` for the two maps in forward order).
- RTDL helper load time was `~21.0 s`, but this path uses packed helper loading/caching behavior and should not be promoted as a broad parser/process-wall claim without a cold/warm protocol.

Not allowed:

- No broad RTDL speedup claim.
- No full Section 5.2 six-pair claim.
- No exact-paper-input claim.
- No full Section 5.7 overlay/PIP claim.
- No generic-language proof.

## Goal-Level Decision Audit

1. Was the earlier six-pair chase foolish after the user changed the rule?
   Yes. Continuing to hunt all six would have been a looks-busy loop.

2. What action would have made the decision foolish?
   Treating missing exact CDBs as a reason to keep searching indefinitely, or treating bigger current OSM data as automatically more scientific.

3. Was there another path?
   Yes: select one representative with an explicit provenance label and finish the comparison.

4. Did this work now follow the better path?
   Mostly yes. One mistake occurred: the first RTDL script used the generic segment kernel, which exposed a real semantic mismatch. The correction was to use the released v2.14 bundled RayJoin LSI helper for Section 5.2 semantics.

## Exit Label

`completed_one_representative_lsi_route__current_osm_geofabrik_lkau_pkau__rtdl_helper_count_matches_authorpatch__no_broad_claim`
