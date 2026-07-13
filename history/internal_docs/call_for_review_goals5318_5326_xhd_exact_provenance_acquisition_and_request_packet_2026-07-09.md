# Call For Review: Goals5318-5326 X-HD Exact Provenance, Acquisition, And Request Packet

Please strictly review the combined X-HD exact-provenance blocker packet.

This packet covers Goals5318-5326. Goal5327 was later added as a narrow
ACM-supplement public-metadata follow-up; review it separately or use the
Goal5318-5327 packet if present.

This packet covers:

```text
Goal5318 WaterBodies/BG exact-provenance search
Goal5319 graphics exact-provenance search
Goal5320 County-ZCTA source/conversion investigation
Goal5321 OSM Lakes/Parks/AllNodes provenance search
Goal5322 BraTS2020 access/conversion provenance
Goal5323 public author repo artifact availability sweep
Goal5324 exact-input acquisition/equivalence decision packet
Goal5325 public web / ACM supplement sweep
Goal5326 external artifact request package
```

## Files To Review

Primary packet files:

```text
history/internal_docs/call_for_review_goals5318_5324_xhd_exact_provenance_blocker_and_acquisition_decision_packet_2026-07-09.md
history/internal_docs/call_for_review_goal5325_xhd_public_web_supplement_artifact_sweep_2026-07-09.md
history/internal_docs/call_for_review_goal5326_xhd_external_artifact_request_package_2026-07-09.md
```

Primary artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5320_county_zcta_source_conversion_investigation.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5322_brats2020_access_conversion_provenance.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5323_external_author_artifact_availability_sweep.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5325_public_web_supplement_artifact_sweep.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5326_external_artifact_request_package.json
```

Goal result reports:

```text
history/internal_docs/goal5318_xhd_water_bg_exact_provenance_search_result_2026-07-09.md
history/internal_docs/goal5319_xhd_graphics_exact_provenance_search_result_2026-07-09.md
history/internal_docs/goal5320_xhd_county_zcta_source_conversion_investigation_result_2026-07-09.md
history/internal_docs/goal5321_xhd_osm_lakes_parks_allnodes_provenance_result_2026-07-09.md
history/internal_docs/goal5322_xhd_brats2020_access_conversion_provenance_result_2026-07-09.md
history/internal_docs/goal5323_xhd_external_author_artifact_availability_sweep_result_2026-07-09.md
history/internal_docs/goal5324_xhd_exact_input_acquisition_and_equivalence_decision_packet_result_2026-07-09.md
history/internal_docs/goal5325_xhd_public_web_supplement_artifact_sweep_result_2026-07-09.md
history/internal_docs/goal5326_xhd_external_artifact_request_package_result_2026-07-09.md
```

## Packet Thesis

Current X-HD status:

```text
Strong Level-B public/source-matched evidence exists.
Exact paper input identity is still not proven.
Full X-HD paper reproduction is not complete.
The public author repo provides source/scripts/logs, not datasets.
The broader web sweep found no public exact dataset artifact.
ACM `ics26-106.zip` remains unresolved due HTTP 403 from this environment.
The next progress requires external artifacts, byte-identical regeneration, or
explicit exact-equivalence acceptance.
```

Therefore:

```text
more route/performance work is not the next paper-reproduction step while input
identity is unchanged.
```

## Review Questions

1. Does the packet correctly establish exact input identity as the current
   blocker?
2. Does it correctly keep WaterBodies/BG, graphics, County/ZCTA, OSM, and BraTS
   evidence below exact-paper status?
3. Does Goal5323 sufficiently answer whether the public author repo already
   contains the missing data?
4. Does Goal5325 correctly leave `ics26-106.zip` unresolved pending ACM access
   or confirmation?
5. Does Goal5324 provide the right decision exits for author artifacts,
   regeneration, exact-equivalence acceptance, or Level-B stop?
6. Does Goal5326 provide a concrete and complete request package for the next
   external step?
7. Is it correct that POD should not be used again until concrete artifacts or
   an accepted public reconstruction appear?
8. Are all forbidden claims preserved: no exact dataset, no Figure 5, no full
   paper, no author-vs-RTDL ratio?
9. Is WaterBodies/BG correctly named as the best optional exact-equivalence
   candidate without self-promoting it to exact?
10. Is the packet ready to send for owner/external review?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5326_xhd_exact_provenance_acquisition_and_request_packet
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
