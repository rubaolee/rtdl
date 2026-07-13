# Call For Review: Goal5340 X-HD Mapped-Candidate Output Comparator

Please strictly review Goal5340.

This goal adds the post-execution comparator for a future mapped-candidate
same-input POD gate. It does not execute author or RTDL commands and does not
claim same-input correctness, exact paper dataset reproduction, Figure 5
reproduction, full paper reproduction, or performance parity.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/compare_xhd_mapped_candidate_same_input_outputs.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5340_mapped_candidate_output_comparison.json
tests/goal5340_xhd_mapped_candidate_output_comparator_test.py
history/internal_docs/goal5340_xhd_mapped_candidate_output_comparator_result_2026-07-09.md
```

## Summary

Goal5340 reads a Goal5339 command packet after a later POD goal has produced
author and RTDL JSON outputs. It compares `HDResult` with explicit tolerance and
records author/RTDL timing fields separately.

Classification outputs:

```text
mapped_candidate_same_input_gate_passed
mapped_candidate_same_input_gate_failed
mapped_candidate_outputs_missing
packet_not_ready_for_output_comparison
```

The pass classification is only a same-input `HDResult` value gate. It is not an
exact paper input identity claim and not a performance claim.

## Validation

```text
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5340_mapped_candidate_output_comparison.json
json.tool OK

py -m unittest tests.goal5340_xhd_mapped_candidate_output_comparator_test
Ran 5 tests OK

py -m unittest tests.goal5339_xhd_mapped_candidate_same_input_packet_test tests.goal5340_xhd_mapped_candidate_output_comparator_test
Ran 9 tests OK
```

## Review Questions

1. Is it correct that Goal5340 is a post-execution comparator, not an executor?
2. Does the comparator fail closed when the Goal5339 packet is not command-ready?
3. Does it fail closed when author or RTDL JSON outputs are missing?
4. Does it compare `HDResult` using explicit tolerance and report pass/fail
   correctly?
5. Does it keep author timing and RTDL timing separated without reporting an
   author-vs-RTDL performance ratio?
6. Is the claim boundary complete: no exact paper dataset reproduction, no
   Figure 5 reproduction, no full paper reproduction, and no performance ratio?
7. Is it correct that this goal does not require POD and that POD belongs only
   to a later command-execution goal after accepted mapping and materialized
   candidate files exist?
8. Are the tests sufficient for this comparator-only scope?
9. Is Goal5340 ready to close as
   `mapped_candidate_same_input_output_comparator_ready__await_real_pod_outputs`?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve_goal5340_mapped_candidate_output_comparator
or
Verdict: approve_with_required_amendments
or
Verdict: block_goal5340

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
