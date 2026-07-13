# Call For Review: Goals5318-5336 X-HD External Provenance Request, Intake, Planning, Refresh, ACM Inspection, And Artifact-Ingestion Packet

Please strictly review the combined X-HD external provenance packet through
Goal5336.

This packet covers:

```text
Goal5318-5325 exact-provenance and public artifact searches
Goal5326 external artifact request package
Goal5327 ACM supplement public-metadata follow-up
Goal5328 external request outbox
Goal5329 external response intake protocol
Goal5330 external response intake validator
Goal5331 synthetic response validation matrix
Goal5332 external response ingest runner
Goal5333 provenance-ingestion action planner
Goal5334 public artifact refresh
Goal5335 ACM supplement zip inspector
Goal5336 ACM artifact-instruction ingestion manifest
```

## Files To Review

Latest packet files:

```text
history/internal_docs/call_for_review_goals5318_5335_xhd_external_provenance_request_intake_validation_planning_refresh_and_acm_inspection_packet_2026-07-09.md
history/internal_docs/call_for_review_goal5336_xhd_acm_artifact_instruction_ingestion_2026-07-09.md
```

Goal5336 primary files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_acm_artifact_instructions.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5336_acm_artifact_instruction_ingestion.json
tests/goal5336_xhd_acm_artifact_instruction_ingestion_test.py
history/internal_docs/goal5336_xhd_acm_artifact_instruction_ingestion_result_2026-07-09.md
```

## Packet Thesis

Current X-HD status:

```text
Strong Level-B public/source-matched evidence exists.
Exact paper input identity is still not proven.
Full X-HD paper reproduction is not complete.
Fresh public artifact refresh still finds no exact input dataset, hash manifest,
byte-identical regeneration script, or public mirror.
ACM ics26-106.zip remains visible but unresolved.
If a reviewer obtains that zip, the project now has:
  a local inspector to produce normalized intake JSON;
  an artifact-instruction ingestion manifest builder that computes per-entry
  hashes and chooses the next follow-up gate.
```

Therefore:

```text
The next real full-reproduction progress requires a real validated external
response or ACM zip inspection. Synthetic zip tests do not inspect the real ACM
supplement and do not change paper-reproduction status.
```

## Review Questions

1. Does this packet correctly establish that exact-input provenance remains the
   blocker?
2. Do Goals5326-5336 materially improve readiness for a future positive
   response or ACM zip access?
3. Does Goal5336 correctly classify artifact-like zip entries without claiming
   exact input identity?
4. Are POD triggers correctly deferred until candidate bytes/hashes/scripts are
   mapped to paper workloads and reviewed?
5. Are all exact/full-paper/Figure/performance claim boundaries preserved?
6. Is the packet ready for owner/external review?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5336_xhd_external_provenance_request_intake_validation_planning_refresh_acm_inspection_and_artifact_ingestion_packet
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
6. ...
```
