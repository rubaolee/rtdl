# Call For Review - Goal5310 X-HD WaterBodies -> BlockGroups Full-Public WKT Candidate

Date: 2026-07-09

Please strictly review Goal5310.

## Files To Review

```text
history/internal_docs/goal5310_xhd_water_bg_full_public_wkt_candidate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5310_water_bg_full_public_wkt_candidate.py
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/manifest.json
tests/goal5310_xhd_water_bg_full_public_wkt_candidate_test.py
```

The generated WKT files are large; inspect hashes/metadata through the
manifest unless a direct file check is needed:

```text
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/USADetailedWaterBodies.wkt.full_public_arcgis_candidate.wkt
Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/USACensusBlockGroupBoundaries.wkt.full_public_arcgis_candidate.wkt
```

## Context

Goal5309 found that WaterBodies and BlockGroups are the strongest full-public
geo candidates:

```text
WaterBodies: +6,129 points (+0.0269%) vs paper log, MBR matches
BlockGroups: +127 points (+0.000243%) vs paper log, MBR matches
```

Goal5310 materializes those public ArcGIS services into full WKT. It does not
run author `hd_exec` or RTDL.

## Review Questions

1. Does the generator correctly materialize one WKT geometry per feature and
   preserve the app-owned author-loader contract?
2. Is the checkpoint/resume behavior safe enough for large generated WKT
   files, including fail-closed behavior when checkpoint and output file
   disagree?
3. Do the manifest and checkpoints prove that both full services were complete,
   not sampled?
4. Are file sizes, sha256 hashes, point counts, and MBR deltas recorded
   sufficiently for the next author ingestion gate?
5. Is it correct to mark `author_hd_exec_ready=true` and `rtdl_route_ready=true`
   only in the limited sense that complete WKT inputs now exist?
6. Does the report correctly avoid exact paper dataset, Figure-5, correctness,
   performance, and full-paper claims?
7. Is the next allowed goal correctly identified as author `hd_exec` ingestion
   on this full-public candidate before RTDL comparison?
8. Are the tests sufficient to protect the conversion contract and claim
   boundary?
9. Should Goal5310 be closed as
   `completed_water_bg_full_public_wkt_candidate_ready_for_author_gate`?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to Q1-Q9:
```

Requested verdict label if approved:

```text
approve_goal5310_water_bg_full_public_wkt_candidate_ready_for_author_gate
```
