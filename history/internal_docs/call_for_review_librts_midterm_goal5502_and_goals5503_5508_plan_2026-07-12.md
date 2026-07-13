# Call For Review: LibRTS Midterm And Completion Plan

Please strictly review the LibRTS paper-app midterm report and the proposed
Goals5503-5508 plan before implementation continues. This is a planning and
evidence-boundary review. No new RTDL core implementation is requested before
the review is resolved.

## Files

```text
history/internal_docs/midterm_report_and_plan_librts_author_validity_after_goal5502_2026-07-12.md
history/internal_docs/goal5501_librts_project_closeout_mismatch_diagnosis_result_2026-07-12.md
history/internal_docs/goal5502_librts_author_validity_gate_result_2026-07-12.md
Paper-reproduction-apps/librts-paper/data/manifest.json
Paper-reproduction-apps/librts-paper/results/goal5501/mismatch_diagnostic.json
Paper-reproduction-apps/librts-paper/results/goal5502/mismatch_diagnostic_250k.json
Paper-reproduction-apps/librts-paper/results/goal5502/author_validity_gate.json
Paper-reproduction-apps/librts-paper/run_goal5502_librts_author_validity_gate.py
tests/goal5502_librts_author_validity_gate_test.py
tests/goal5502_librts_author_validity_result_test.py
```

## Review Questions

1. Does the midterm report accurately separate bounded count agreement,
   relation equality, capacity, numerical contract, and performance?
2. Is the official archive provenance and exact-input status represented
   correctly without upgrading the result to full paper reproduction?
3. Does the Goal5502 evidence accurately show RTDL matching the selected CPU
   float32 contract on all five prefixes, with author agreement on one and
   divergence on four?
4. Is CPU float64 correctly treated as a diagnostic rather than silently
   selected as the truth or used to accuse either implementation?
5. Does the report correctly refuse to call the author wrong from count
   differences alone?
6. Is the rule `author == oracle and RTDL != oracle -> fix RTDL` sufficiently
   precise and appropriately limited to the validated contract?
7. Is the rule `RTDL == oracle and author != oracle -> preserve RTDL` compatible
   with RTDL's generic-system principle?
8. Does the plan keep author parsing, WKT, provenance, cache policy, and
   compatibility behavior app-owned?
9. Are Goals5503-5508 ordered correctly, with contract audit and independent
   oracle work before any RTDL semantic change or performance claim?
10. Does Goal5505 define a scalable oracle without silently turning a sample
    into full-input evidence?
11. Does Goal5506 keep `parks.bz2` CUDA OOM as a capacity question separate
    from the semantic mismatch question?
12. Does Goal5507 provide a real decision gate rather than another route-tuning
    sequence?
13. Are the proposed success outcomes complete and mutually distinguishable?
14. Does the plan preserve the no-Embree rule and the no-author-performance-
    ratio rule?
15. Are any required amendments needed before implementing Goal5503?

## Required Review Focus

Please pay particular attention to these risks:

- treating a CPU float32 oracle as authoritative without first documenting
  the author contract;
- declaring the author wrong from a count mismatch without pair rows or source
  semantics;
- changing RTDL defaults to imitate an app-specific implementation detail;
- using a larger prefix as if it were a full-input adjudication;
- spending more work on performance before correctness and capacity contracts
  are aligned;
- allowing the `parks.bz2` OOM to disappear into a semantic claim.

## Authorized Current Claim

The only current authorized claim is:

```text
On five same-source prefixes, RTDL matches the selected independent inclusive
float32 AABB contract. The author matches one prefix and diverges on four.
This is prefix evidence only; it does not prove full-input author validity,
full-input RTDL correctness, complete range-intersects coverage, relation
parity, performance parity, full paper reproduction, zero-copy, or Embree.
The evidence currently authorizes no RTDL core semantic change and no
author-specific behavior in RTDL core.
```

## Forbidden Summaries

```text
the author is definitively wrong on the full dataset
RTDL has fully reproduced LibRTS
all range-intersects results match
RTDL matches the author on every input
RTDL is faster than the author
FP64 proves either side correct
parks.bz2 OOM is resolved
full paper reproduction complete
```

## Requested Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to review questions 1-15:
Goal5502 decision:
Goals5503-5508 plan decision:
RTDL genericity decision:
POD/resource decision:
Requested verdict label:
```
