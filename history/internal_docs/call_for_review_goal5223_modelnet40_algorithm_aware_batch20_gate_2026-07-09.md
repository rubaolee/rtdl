# Call For Review: Goal5223 ModelNet40 Algorithm-Aware Batch20 Gate

Date: 2026-07-09

Please strictly review Goal5223:

```text
history/internal_docs/goal5223_modelnet40_algorithm_aware_batch20_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5223_modelnet40_algorithm_aware_batch20_summary_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5223_modelnet40_algorithm_aware_batch20_artifacts_2026-07-09.tar.gz
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_modelnet40_normalized_batch_gate.py
tests/goal5223_modelnet40_algorithm_aware_comparator_test.py
```

## Context

Goal5221 had a 19/20 result because it used current author `main/rt` for every
selected ModelNet40 paper-log record. Goal5222 showed that the single failing
`range_hood` case was a comparator-regime mismatch: the paper log reports
`Algorithm=Hybrid`, and the paper-branch `variant=hybrid` comparator matches
that paper log exactly.

Goal5223 modifies the app-owned batch runner so comparator selection follows
the paper-log algorithm payload extracted from the original author log blob.

## Review Questions

1. Does the implementation select author comparator by paper-log algorithm
   payload rather than by a hardcoded `range_hood` exception?
2. Does the 20-case POD summary show `selected_count=20`,
   `matched_case_count=20`, and `all_cases_matched=true`?
3. Do all 20 selected records use the paper-log `Algorithm=Hybrid` and
   paper-branch `variant=hybrid` comparator?
4. Is the `range_hood` case now correctly matched against paper-branch Hybrid
   and RTDL within tolerance?
5. Does the runner remain app-owned without adding ModelNet40/X-HD semantics to
   RTDL core?
6. Are the tests sufficient for the algorithm-aware comparator selection logic?
7. Does the report avoid claiming all ModelNet40 reproduction, exact byte
   identity, full X-HD paper reproduction, or author-vs-RTDL performance ratio?
8. Is the proposed next step reasonable: either expand ModelNet40 coverage with
   the same algorithm-aware comparator, or freeze this as a representative
   Level-B batch and move to another workload family?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
2. ...
...
8. ...
```

Requested verdict label if approved:

```text
approve_goal5223_modelnet40_algorithm_aware_batch20_gate
```
