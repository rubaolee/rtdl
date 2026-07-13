# Call For Review: Goal5333 X-HD Provenance Ingestion Action Planner

Please strictly review Goal5333.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/plan_xhd_provenance_ingestion_from_case.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5333_provenance_ingestion_action_planner.json
tests/goal5333_xhd_provenance_ingestion_action_planner_test.py
history/internal_docs/goal5333_xhd_provenance_ingestion_action_planner_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_external_response.py
Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py
Paper-reproduction-apps/x-hd-paper/requests/examples/
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5332_external_response_ingest_runner.json
```

## Goal5333 Summary

Goal5333 implements:

```text
plan_xhd_provenance_ingestion_from_case.py
```

The planner reads a case directory produced by Goal5332 and emits:

```text
provenance_action_plan.json
provenance_action_plan.md
```

when `--write` is supplied.

It maps validated cases to follow-up goal types such as:

```text
author_archive_provenance_ingestion_gate
byte_identical_regeneration_provenance_gate
accepted_exact_equivalence_bounded_matrix_gate
request_missing_material_or_record_blocked_status
```

It does not run POD. It requires a separate provenance-ingestion goal before
POD or any claim update.

## Review Questions

1. Is it correct to add a planner between response ingestion and POD work?
2. Does the planner preserve the Goal5330/5332 validation boundaries?
3. Are positive responses mapped to appropriate follow-up goal types?
4. Are hash-only, no-artifact, non-availability, invalid, and inconsistent
   cases fail-closed?
5. Is `requires_new_goal_before_pod=true` correct?
6. Are POD triggers correctly deferred?
7. Are claim boundaries complete?
8. Is the result ready to join the broader Goals5318-5333 external provenance
   packet?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5333_provenance_action_planner_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5333

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
