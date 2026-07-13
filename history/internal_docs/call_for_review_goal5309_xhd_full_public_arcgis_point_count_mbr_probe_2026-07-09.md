# Call For Review - Goal5309 X-HD Full-Public ArcGIS Point-Count / MBR Probe

Date: 2026-07-09

Please strictly review Goal5309.

## Files To Review

```text
history/internal_docs/goal5309_xhd_full_public_arcgis_point_count_mbr_probe_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5309_full_public_arcgis_point_count_mbr_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_full_public_arcgis_probe_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_county_full_arcgis_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_zcta_full_arcgis_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_waterbodies_full_arcgis_probe_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5309_blockgroups_full_arcgis_probe_2026-07-09.json
tests/goal5309_xhd_full_public_arcgis_probe_contract_test.py
tests/goal5309_xhd_full_public_arcgis_probe_result_test.py
```

## Context

Goal5308 blocked geo Figure-5 claims because exact author WKT files are
unavailable. Goal5309 is the authorized next step: page the public ArcGIS
name-matched services and compare author-loader point counts / MBRs with the
paper logs before generating full WKT or running author/RTDL.

Goal5309 is **not** a correctness run and **not** a performance run.

## Review Questions

1. Does the probe implement the author-loader point-count contract correctly
   enough for this gate, especially polygon closure versus line/point
   non-closure?
2. Are checkpoint resume, atomic writes, and retry/backoff sufficient for the
   long-running ArcGIS services?
3. Do the four full-public result JSON files prove that all four services were
   fully paged, not just sampled?
4. Is the County classification correct: MBR matches but point count is +32.2%,
   therefore County-ZCTA cannot be promoted to exact paper input or Figure-5
   reproduction?
5. Is the ZCTA classification correct: very close count/MBR, but still no
   exact file/hash provenance?
6. Is the WaterBodies-BlockGroups classification correct: strong full-public
   candidate by count/MBR, but still not exact without file/hash provenance?
7. Does the result correctly avoid author/RTDL correctness and performance
   claims, since no author `hd_exec` or RTDL route ran in Goal5309?
8. Is the next allowed action correct: investigate alternate County
   source/simplification before County-ZCTA Figure-5 work, while optionally
   preparing a reviewed full-public WaterBodies-BlockGroups author/RTDL gate?
9. Are the tests strong enough to pin both the helper contract and the result
   claim boundary?
10. Should Goal5309 be closed as
    `completed_full_public_arcgis_probe__county_blocks_exact_geo_claim__water_bg_strong_candidate`?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to Q1-Q10:
```

Requested verdict label if approved:

```text
approve_goal5309_full_public_arcgis_probe__county_mismatch_blocks_exact__water_bg_candidate
```
