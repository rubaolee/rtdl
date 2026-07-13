# Call For Review: Goal5484

Please strictly review the Goal5484 Figure-6 denominator audit against the
source script and its three input evidence artifacts.

## Files to inspect

- `Paper-reproduction-apps/librts-paper/audit_exact_figure6_point_contains_denominator.py`
- `tests/goal5484_librts_exact_figure6_denominator_audit_test.py`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5472_author_paper_log_denominators.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5481_exact_point_contains.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5482_exact_point_contains_remaining_batch.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5484_exact_figure6_point_contains_denominator.json`
- `history/internal_docs/goal5484_librts_exact_figure6_point_contains_denominator_audit_result_2026-07-11.md`

## Review questions

1. Does the selector restrict records to paper Figure 6, the 100K
   point-contains category, and `rtspatial` rather than mixing backends or
   query sizes?
2. Does it require exactly the six intended dataset records and reject missing
   or duplicate records?
3. Does every exact gate match the corresponding author record on geometry
   count, query count, and result count?
4. Does the audit preserve the distinction between the six exact-input count
   gates and a reproduced Figure-6 plot?
5. Is the author timing denominator correctly described as internal Query Time
   with Loading Time excluded?
6. Does the result explicitly refuse an author/RTDL performance ratio because
   RTDL route wall is not the same denominator?
7. Is the audit app-owned bookkeeping over existing evidence, with no RTDL
   core or LibRTS-specific primitive added?
8. Do the tests exercise record selection, mismatch rejection, and the closed
   performance boundary behaviorally?
9. Are complete-paper, pair-row, author-equivalence, speedup, and Embree claims
   all left closed?
10. What amendments, if any, are required before Goal5484 can be externally
    reviewed and approved?

## Expected answer shape

```text
Verdict: approve | approve_with_required_amendments | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
Answers 1-10: ...
```
