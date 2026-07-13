# Call For Review: Goal5332 X-HD External Response Ingest Runner

Please strictly review Goal5332.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_external_response.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5332_external_response_ingest_runner.json
tests/goal5332_xhd_external_response_ingest_runner_test.py
history/internal_docs/goal5332_xhd_external_response_ingest_runner_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py
Paper-reproduction-apps/x-hd-paper/requests/incoming/README.md
Paper-reproduction-apps/x-hd-paper/requests/examples/
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5330_external_response_intake_validator.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5331_external_response_validation_matrix.json
```

## Goal5332 Summary

Goal5332 implements:

```text
ingest_xhd_external_response.py
```

The runner ingests a normalized external response JSON into:

```text
Paper-reproduction-apps/x-hd-paper/requests/incoming/<case-id>/
```

and writes:

```text
response.json
validation_result.json
manifest.json
next_action.md
```

It reuses the Goal5330 validator. It does not send requests, download
artifacts, run POD, or change any reproduction claim.

## Review Questions

1. Is it correct to add an executable intake runner instead of leaving response
   handling purely manual?
2. Does the runner reuse Goal5330 validator behavior rather than introducing a
   second classification policy?
3. Is the output layout auditable and deterministic enough?
4. Are exit codes correct and fail-closed?
5. Is it correct that invalid/template responses are still recorded for audit?
6. Is the duplicate-case default of "fail unless --overwrite" correct?
7. Are POD triggers correctly deferred to a later provenance-ingestion goal?
8. Are claim boundaries complete?
9. Is the result ready to join the broader Goals5318-5332 external provenance
   packet?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5332_external_response_ingest_runner_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5332

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
9. ...
```
