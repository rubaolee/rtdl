# Call For Review: Goal5338 X-HD Candidate Workload Mapping Review Gate

Please strictly review Goal5338.

## Files To Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/review_xhd_candidate_workload_mapping.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5338_candidate_workload_mapping_review.json
tests/goal5338_xhd_candidate_workload_mapping_review_test.py
history/internal_docs/goal5338_xhd_candidate_workload_mapping_review_result_2026-07-09.md
```

Supporting context:

```text
Paper-reproduction-apps/x-hd-paper/scripts/map_xhd_acm_candidate_bytes_hashes.py
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
history/internal_docs/goal5337_xhd_acm_candidate_hash_mapping_result_2026-07-09.md
```

## Goal5338 Summary

Goal5338 implements:

```text
review_xhd_candidate_workload_mapping.py
```

The script validates that cleanly hashed candidate ACM files are mapped to
known X-HD paper workload roles before any same-input POD gate is allowed.

It distinguishes:

```text
accepted_workload_mapping_ready_for_same_input_gate
proposed_workload_mapping_requires_external_acceptance
workload_mapping_invalid_or_incomplete
```

It does not run POD or claim exact paper reproduction.

## Review Questions

1. Is it correct to add a candidate workload mapping gate after Goal5337?
2. Is the mapping spec contract sufficient for a later same-input POD goal?
3. Is validating dataset names against the paper target matrix correct?
4. Is it correct that proposed mappings do not allow POD?
5. Is it correct that accepted clean mappings allow only a later separate POD
   goal, not direct exact/full reproduction claims?
6. Do dirty candidate hash mappings and unknown paper dataset names fail
   closed?
7. Are claim boundaries complete?
8. Is the result ready to join the broader Goals5318-5338 external provenance
   packet?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5338_candidate_workload_mapping_review_ready
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5338

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
