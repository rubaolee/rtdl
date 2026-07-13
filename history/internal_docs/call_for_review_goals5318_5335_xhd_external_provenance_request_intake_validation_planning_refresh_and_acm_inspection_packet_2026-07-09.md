# Call For Review: Goals5318-5335 X-HD External Provenance Request, Intake, Planning, Refresh, And ACM Inspection Packet

Please strictly review the combined X-HD external provenance packet through
Goal5335.

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
```

## Files To Review

Latest packet files:

```text
history/internal_docs/call_for_review_goals5318_5334_xhd_external_provenance_request_intake_validation_planning_and_refresh_packet_2026-07-09.md
history/internal_docs/call_for_review_goal5335_xhd_acm_supplement_zip_inspector_2026-07-09.md
```

Goal5335 primary files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_acm_supplement_zip.py
Paper-reproduction-apps/x-hd-paper/scripts/plan_xhd_provenance_ingestion_from_case.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5335_acm_supplement_zip_inspector.json
tests/goal5335_xhd_acm_supplement_zip_inspector_test.py
history/internal_docs/goal5335_xhd_acm_supplement_zip_inspector_result_2026-07-09.md
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
If a reviewer obtains that zip, the project now has a local inspector that can
produce normalized intake JSON for the existing validator/ingest/planner chain.
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
2. Do Goals5326-5335 materially improve readiness for a future positive
   response or ACM zip access?
3. Does Goal5335 correctly turn a future ACM zip into normalized intake JSON?
4. Are POD triggers correctly deferred until artifact instructions have been
   ingested into concrete input bytes/hashes/regeneration/equivalence criteria?
5. Are all exact/full-paper/Figure/performance claim boundaries preserved?
6. Is the packet ready for owner/external review?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5335_xhd_external_provenance_request_intake_validation_planning_refresh_and_acm_inspection_packet
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
