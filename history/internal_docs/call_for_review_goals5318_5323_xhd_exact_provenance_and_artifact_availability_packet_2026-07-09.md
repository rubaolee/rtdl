# Call For Review: Goals5318-5323 X-HD Exact Provenance And Artifact Availability Packet

Please strictly review the current X-HD exact-input blocker packet.

This packet supersedes the narrower Goals5318-5322 packet by adding Goal5323's
cross-cutting public author repository / artifact availability sweep.

## Files To Review

Goal5318:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
tests/goal5318_xhd_water_bg_exact_provenance_search_test.py
history/internal_docs/goal5318_xhd_water_bg_exact_provenance_search_result_2026-07-09.md
history/internal_docs/call_for_review_goal5318_xhd_water_bg_exact_provenance_search_2026-07-09.md
```

Goal5319:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
tests/goal5319_xhd_graphics_exact_provenance_search_test.py
history/internal_docs/goal5319_xhd_graphics_exact_provenance_search_result_2026-07-09.md
history/internal_docs/call_for_review_goal5319_xhd_graphics_exact_provenance_search_2026-07-09.md
```

Goal5320:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5320_county_zcta_source_conversion_investigation.json
tests/goal5320_xhd_county_zcta_source_conversion_investigation_test.py
history/internal_docs/goal5320_xhd_county_zcta_source_conversion_investigation_result_2026-07-09.md
history/internal_docs/call_for_review_goal5320_xhd_county_zcta_source_conversion_investigation_2026-07-09.md
```

Goal5321:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
tests/goal5321_xhd_osm_lakes_parks_allnodes_provenance_test.py
history/internal_docs/goal5321_xhd_osm_lakes_parks_allnodes_provenance_result_2026-07-09.md
history/internal_docs/call_for_review_goal5321_xhd_osm_lakes_parks_allnodes_provenance_2026-07-09.md
```

Goal5322:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5322_brats2020_access_conversion_provenance.json
tests/goal5322_xhd_brats2020_access_conversion_provenance_test.py
history/internal_docs/goal5322_xhd_brats2020_access_conversion_provenance_result_2026-07-09.md
history/internal_docs/call_for_review_goal5322_xhd_brats2020_access_conversion_provenance_2026-07-09.md
```

Goal5323:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5323_external_author_artifact_availability_sweep.json
tests/goal5323_xhd_external_author_artifact_availability_test.py
history/internal_docs/goal5323_xhd_external_author_artifact_availability_sweep_result_2026-07-09.md
history/internal_docs/call_for_review_goal5323_xhd_external_author_artifact_availability_sweep_2026-07-09.md
```

## Packet Summary

This packet asks whether the current project can honestly upgrade any current
Figure-5-like X-HD line from Level-B public/source-matched evidence to exact
paper dataset reproduction.

Current row-level conclusions:

```text
Goal5318 WaterBodies/BG:
  exit = water_bg_exact_provenance_not_found_keep_level_b

Goal5319 graphics:
  exit = graphics_exact_provenance_not_found_keep_level_b

Goal5320 County/ZCTA:
  exit = county_zcta_exact_provenance_not_found__source_conversion_blocked

Goal5321 OSM Lakes/Parks/AllNodes:
  exit = osm_lakes_parks_allnodes_exact_provenance_not_found__snapshot_filter_blocked

Goal5322 BraTS2020:
  exit = brats2020_exact_provenance_not_found__access_and_conversion_blocked

Goal5323 public author repository / artifacts:
  exit = external_author_dataset_artifacts_not_found__repo_source_logs_only
```

Allowed current summary:

```text
The current X-HD work has strong Level-B evidence for several public/source-
matched rows and a substantial generic RTDL route/system extraction. However,
full paper reproduction remains blocked because exact paper input files,
hashes, byte-identical regeneration proof, or externally accepted exact-
equivalence decisions are still absent. The public author repository provides
source, scripts, and checked-in logs, not the missing exact datasets.
```

Forbidden summaries:

```text
X-HD full paper reproduction is complete.
Figure 5 is reproduced.
Public Stanford / ArcGIS / SpatialHadoop / BraTS sources are proven exact author
inputs.
Checked-in author logs are exact input files.
The public GitHub repository contains the missing HDDatasets.
Author-vs-RTDL performance ratios are authorized from this provenance packet.
```

## Review Questions

1. Do Goals5318-5323 together correctly distinguish Level-B source-matched
   evidence from Level-C exact paper input reproduction?
2. Is the exact-input rule correct: paths, point counts, MBRs, HDResult matches,
   public source names, logs, and statistics are insufficient without file/hash,
   byte-identical regeneration, or explicit external acceptance?
3. Does Goal5323 correctly close the obvious "maybe the public repo has the
   data" question by classifying the author repo as source/scripts/logs only?
4. Is WaterBodies/BG correctly kept at Level-B despite strong evidence
   (near counts/MBRs, paper-config author scalar, RTDL float64/author float32
   alignment)?
5. Is graphics correctly kept at Level-B despite value-matched public Stanford
   rows and app-owned scaled candidates?
6. Is County/ZCTA correctly classified as source/conversion blocked because the
   County point count/source does not align?
7. Is OSM correctly classified as snapshot/filter/conversion blocked?
8. Is BraTS correctly classified as access/conversion blocked rather than a POD
   or RTDL route problem?
9. Does the packet correctly avoid author-vs-RTDL performance ratios and Figure
   reproduction claims?
10. Should the next work be external input acquisition / external review of
    exact-equivalence rather than more route performance work?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5323_xhd_exact_provenance_blocker_packet
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
