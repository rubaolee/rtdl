# Call For Review: Goal5485

Please strictly review the Goal5485 prepared-index phase gate and its live POD
result. The POD result is exact-input count evidence and a phase-boundary
measurement candidate; it is not an authorized performance ratio.

## Files

- `Paper-reproduction-apps/librts-paper/run_exact_point_contains_prepared_phase_gate.py`
- `tests/goal5485_librts_exact_point_contains_prepared_phase_gate_test.py`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5481_exact_point_contains.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5484_exact_figure6_point_contains_denominator.json`
- `history/internal_docs/goal5485_librts_exact_point_contains_prepared_phase_gate_result_2026-07-11.md`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5485_dtl_cnty_prepared_phase.json`

## Review questions

1. Does the gate use the existing generic `prepare_aabb_index_2d` and
   `prepared.count` APIs without adding LibRTS-specific core behavior?
2. Are WKT loading, index preparation, prepared query, and primitive query
   timings recorded as separate fields?
3. Does the author Query Time boundary remain explicitly separate from Loading
   Time?
4. Does the gate avoid row output and preserve the count-only limitation?
5. Does it close the prepared handle even if the query path raises?
6. Is `prepared_query_phase_comparison_candidate` correctly weaker than an
   authorized performance ratio?
7. Does the test behaviorally prove that the one-shot query helper is not used?
8. Does the live POD probe use the verified official archive members and match
   the author result count on the same files?
9. Are Figure-6, full-paper, pair-row, performance-ratio, and Embree claims
   all closed?
10. Are the phase numbers recorded without author-vs-RTDL ratio overclaim, and
    what amendments are required before the result can be accepted?

## Expected answer shape

```text
Verdict: approve | approve_with_required_amendments | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
Answers 1-10: ...
```
