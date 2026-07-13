# Call For Review: Goals5318-5324 X-HD Exact Provenance Blocker And Acquisition Decision Packet

Please strictly review the current X-HD exact-provenance blocker and acquisition
decision packet.

This packet extends Goals5318-5323 with Goal5324's concrete acquisition and
exact-equivalence decision protocol.

## Files To Review

Primary packet files:

```text
history/internal_docs/call_for_review_goals5318_5323_xhd_exact_provenance_and_artifact_availability_packet_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5324_exact_input_acquisition_and_equivalence_decision_packet.json
tests/goal5324_xhd_exact_input_acquisition_packet_test.py
history/internal_docs/goal5324_xhd_exact_input_acquisition_and_equivalence_decision_packet_result_2026-07-09.md
history/internal_docs/call_for_review_goal5324_xhd_exact_input_acquisition_and_equivalence_decision_packet_2026-07-09.md
```

Underlying Goals5318-5323 artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5318_water_bg_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5319_graphics_exact_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5320_county_zcta_source_conversion_investigation.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5321_osm_lakes_parks_allnodes_provenance_search.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5322_brats2020_access_conversion_provenance.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5323_external_author_artifact_availability_sweep.json
```

## Packet Thesis

Current X-HD state:

```text
Strong Level-B public/source-matched evidence exists.
Exact paper dataset reproduction is not proven.
Full X-HD paper reproduction is not complete.
The public author repository provides source/scripts/logs, not exact datasets.
The next full-reproduction step is external input artifacts or an explicit
exact-equivalence decision, not more route optimization.
```

Goal5324 exits:

```text
author files/hashes acquired:
  run author/RTDL same-input gates and performance matrix.

byte-identical regeneration pipeline acquired:
  regenerate, hash, run author/RTDL gates.

external review accepts public reconstruction as exact-equivalent:
  rename claim precisely and run bounded Figure-5 matrix under accepted inputs.

no external artifacts and no exact-equivalence acceptance:
  stop full-paper claims at Level-B.
```

## Review Questions

1. Does the combined packet correctly establish that exact paper input identity
   remains the blocker?
2. Does it avoid overclaiming current Level-B evidence as full paper
   reproduction?
3. Does Goal5323 sufficiently answer the "maybe the public repo has data"
   question?
4. Does Goal5324 provide a complete and actionable acquisition/equivalence
   decision protocol?
5. Is WaterBodies/BG the right first candidate for optional exact-equivalence
   review if owner wants to pursue that route?
6. Should route/performance work pause as paper-reproduction work until input
   identity changes?
7. Are all forbidden claims correctly excluded?
8. Is POD non-use correct until concrete input artifacts appear?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5324_xhd_exact_provenance_and_acquisition_packet
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
8. ...
```
