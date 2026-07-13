# Call For Review: Goal5336 X-HD ACM Artifact-Instruction Ingestion Manifest

Please strictly review Goal5336.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_acm_artifact_instructions.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5336_acm_artifact_instruction_ingestion.json
tests/goal5336_xhd_acm_artifact_instruction_ingestion_test.py
history/internal_docs/goal5336_xhd_acm_artifact_instruction_ingestion_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/inspect_xhd_acm_supplement_zip.py
history/internal_docs/goal5335_xhd_acm_supplement_zip_inspector_result_2026-07-09.md
```

## Goal5336 Summary

Goal5336 implements:

```text
ingest_xhd_acm_artifact_instructions.py
```

The script reads a local ACM supplement zip and emits an ingestion manifest for
artifact-like entries.

It computes per-entry hashes and classifies entries into:

```text
candidate_input_or_archive
hash_or_manifest
script
instruction
```

It then selects a follow-up goal type such as:

```text
acm_candidate_bytes_hash_mapping_gate
acm_candidate_bytes_identity_review
acm_regeneration_or_instruction_review
record_acm_no_actionable_artifact
```

It does not run POD or claim exact paper reproduction.

## Review Questions

1. Is it correct to add an artifact-instruction ingestion manifest builder after
   the ACM zip inspector?
2. Are candidate bytes/hash/script/instruction classifications reasonable and
   conservative?
3. Is per-entry sha256 recording useful and safe?
4. Are follow-up goal types correct?
5. Is it correct that even candidate bytes plus hashes still require a mapping
   gate before POD?
6. Are invalid/no-artifact/script-only cases fail-closed?
7. Are claim boundaries complete?
8. Is it correct that no POD is needed?
9. Is the result ready to join the broader Goals5318-5336 external provenance
   packet?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5336_acm_artifact_instruction_ingestion_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5336

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
