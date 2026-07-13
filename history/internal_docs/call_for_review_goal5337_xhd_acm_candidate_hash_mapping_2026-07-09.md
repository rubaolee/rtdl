# Call For Review: Goal5337 X-HD ACM Candidate Bytes / Hash Mapping Gate

Please strictly review Goal5337.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/map_xhd_acm_candidate_bytes_hashes.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5337_acm_candidate_hash_mapping.json
tests/goal5337_xhd_acm_candidate_hash_mapping_test.py
history/internal_docs/goal5337_xhd_acm_candidate_hash_mapping_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/ingest_xhd_acm_artifact_instructions.py
history/internal_docs/goal5336_xhd_acm_artifact_instruction_ingestion_result_2026-07-09.md
```

## Goal5337 Summary

Goal5337 implements:

```text
map_xhd_acm_candidate_bytes_hashes.py
```

The script reads a local ACM supplement zip, reuses Goal5336 artifact
classification, parses simple SHA256 manifest lines, and reports whether
candidate input/archive entries are covered by matching hashes.

It selects conservative follow-up goal types such as:

```text
candidate_workload_mapping_review
candidate_hash_mismatch_review
candidate_hash_mapping_gap_review
candidate_identity_review
record_no_candidate_bytes
```

It does not run POD or claim exact paper reproduction.

## Review Questions

1. Is it correct to add a candidate bytes/hash mapping gate after Goal5336?
2. Is it correct that candidate bytes plus matching hashes still require
   workload mapping/review before POD?
3. Is parsing simple SHA256 manifest lines sufficient for this bounded gate?
4. Do named hash mismatches fail closed?
5. Are candidate-without-hash and invalid-zip cases conservative?
6. Are claim boundaries complete?
7. Is it correct that no POD is needed?
8. Is the result ready to join the broader Goals5318-5337 external provenance
   packet?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5337_acm_candidate_hash_mapping_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5337

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
