# Call For Review: Goals5318-5332 X-HD External Provenance Request, Intake, Validation, And Ingest Packet

Please strictly review the combined X-HD external provenance packet through
Goal5332.

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
```

## Files To Review

Latest packet files:

```text
history/internal_docs/call_for_review_goals5318_5331_xhd_external_provenance_request_intake_validation_packet_2026-07-09.md
history/internal_docs/call_for_review_goal5332_xhd_external_response_ingest_runner_2026-07-09.md
```

Goal5332 primary files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_external_response.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5332_external_response_ingest_runner.json
tests/goal5332_xhd_external_response_ingest_runner_test.py
history/internal_docs/goal5332_xhd_external_response_ingest_runner_result_2026-07-09.md
```

## Packet Thesis

Current X-HD status:

```text
Strong Level-B public/source-matched evidence exists.
Exact paper input identity is still not proven.
Full X-HD paper reproduction is not complete.
Public repo/web/metadata sweeps did not find exact datasets.
External requests are prepared but not sent by Codex.
Future responses now have:
  a fail-closed intake template;
  an executable validator;
  synthetic examples that lock validator routing behavior;
  an executable ingest runner that records response cases durably.
```

Therefore:

```text
The next real full-reproduction progress requires a real validated external
response before any exact-dataset POD route or performance claim can proceed.
```

## Review Questions

1. Does this packet correctly establish that exact-input provenance remains the
   blocker?
2. Do Goals5326-5332 materially improve readiness for a future positive
   response?
3. Does Goal5332 close the manual gap between a normalized response JSON and an
   auditable intake case?
4. Are POD triggers correctly deferred until a valid positive real response and
   a later provenance-ingestion goal?
5. Are all exact/full-paper/Figure/performance claim boundaries preserved?
6. Is the packet ready for owner/external review?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goals5318_5332_xhd_external_provenance_request_intake_validation_packet
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
