# Call For Review: Goal5324 X-HD Exact Input Acquisition And Equivalence Decision Packet

Please strictly review Goal5324.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
tests/goal5324_xhd_exact_input_acquisition_packet_test.py
history/internal_docs/goal5324_xhd_exact_input_acquisition_and_equivalence_decision_packet_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5317_figure5_exact_input_acquisition_gap_matrix.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5320_county_zcta_source_conversion_investigation.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5322_brats2020_access_conversion_provenance.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5323_external_author_artifact_availability_sweep.json
```

## Goal5324 Summary

Goal5324 converts the exact-input blocker into an action packet.

Core decision:

```text
full_reproduction_next_blocker = exact_input_artifacts_or_explicit_exact_equivalence_acceptance
more_route_performance_work_is_next = false
```

It defines:

```text
1. the author artifact request;
2. required evidence for graphics / geo / BraTS;
3. the public exact-equivalence review protocol;
4. WaterBodies/BG as the best current exact-equivalence candidate if owner wants
   that review;
5. stop/continue exits.
```

Exit label:

```text
exact_input_acquisition_packet_ready__await_external_artifacts_or_equivalence_decision
```

## Review Questions

1. Does Goal5324 correctly translate Goals5318-5323 into an actionable
   acquisition / decision packet rather than another performance goal?
2. Is the author artifact request complete enough for the current X-HD blockers
   (graphics, geo WKT, BraTS)?
3. Is the public exact-equivalence protocol strict enough: source snapshot,
   deterministic conversion, generated hashes, author rerun, RTDL rerun, and
   explicit external acceptance?
4. Does the packet correctly state that counts/MBRs/statistics/HDResult/logs
   alone are insufficient for exact dataset status?
5. Is WaterBodies/BG correctly identified as the best current candidate for an
   optional exact-equivalence review, while still not self-promoted to exact?
6. Is it correct to say more route/performance work is not the next full-paper
   reproduction step until input identity changes?
7. Is the stop/continue matrix complete and honest?
8. Is it correct that no POD is needed for Goal5324?
9. Are claim boundaries complete: no exact input acquisition complete, no Figure
   5, no full paper, no author-vs-RTDL ratio?
10. Should this packet be appended to the Goals5318-5323 exact-provenance
    blocker packet before owner/reviewer decision?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5324_exact_input_acquisition_packet
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5324

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
