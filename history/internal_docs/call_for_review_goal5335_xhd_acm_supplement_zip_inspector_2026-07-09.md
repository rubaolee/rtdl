# Call For Review: Goal5335 X-HD ACM Supplement Zip Inspector

Please strictly review Goal5335.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_acm_supplement_zip.py
Paper-reproduction-apps/x-hd-paper/scripts/plan_xhd_provenance_ingestion_from_case.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5335_acm_supplement_zip_inspector.json
tests/goal5335_xhd_acm_supplement_zip_inspector_test.py
history/internal_docs/goal5335_xhd_acm_supplement_zip_inspector_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/validate_xhd_external_response_intake.py
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_external_response.py
history/internal_docs/goal5325_xhd_public_web_supplement_artifact_sweep_result_2026-07-09.md
history/internal_docs/goal5327_xhd_acm_supplement_public_metadata_followup_result_2026-07-09.md
history/internal_docs/goal5334_xhd_public_artifact_refresh_result_2026-07-09.md
```

## Goal5335 Summary

Goal5335 implements:

```text
inspect_xhd_acm_supplement_zip.py
```

The script inspects a local zip supplied by an owner or ACM-access reviewer and
emits normalized external response intake JSON:

```text
response_type = acm_supplement_artifact_instructions
```

It records zip sha256, file listing, top-level files, and heuristic
dataset/hash/script/instruction entries.

Goal5335 also tightens the Goal5333 planner so artifact-bearing ACM listings
map to:

```text
ready_for_separate_artifact_instruction_ingestion_goal
recommended_goal_type = acm_artifact_instruction_ingestion_gate
pod_allowed_next = false
```

This prevents "ACM has artifact instructions" from being mistaken for "run POD
now."

## Review Questions

1. Is it correct to add a local ACM supplement zip inspector?
2. Does the inspector emit the existing Goal5329 intake schema rather than a new
   response format?
3. Are the no-artifact and artifact-bearing synthetic tests meaningful?
4. Is the heuristic classification conservative enough?
5. Is it correct that artifact-bearing ACM listings lead to an ingestion goal
   before POD, not direct POD?
6. Does the planner change preserve fail-closed behavior?
7. Are claim boundaries complete, especially "synthetic zip tests do not inspect
   the real ACM supplement"?
8. Is it correct that no POD is needed?
9. Is the result ready to join the broader Goals5318-5335 external provenance
   packet?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5335_acm_supplement_zip_inspector_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5335

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
