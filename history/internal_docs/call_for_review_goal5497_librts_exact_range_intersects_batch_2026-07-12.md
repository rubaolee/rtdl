# Call For Review: Goal5497 LibRTS Exact Range-Intersects Batch

Please review Goal5496 and Goal5497 as one bounded exact range-intersects
batch. Verify the two machine-readable gate artifacts directly. Keep the
review count-level: equal counts do not establish pointwise intersection
relation equality.

## Files

- `history/internal_docs/goal5496_librts_exact_range_intersects_dtl_result_2026-07-12.md`
- `history/internal_docs/goal5497_librts_exact_range_intersects_batch_result_2026-07-12.md`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_gate.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5497_range_intersects_dtl_cnty_select0001_gate.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5497_range_intersects_dtl_cnty_select0001_extraction.json`
- `tests/goal5496_librts_exact_range_intersects_count_gate_test.py`
- `tests/goal5497_librts_exact_range_intersects_batch_evidence_test.py`

## Review questions

1. Do both selected pairs appear in the verified Goal5492 inventory?
2. Is the geometry SHA identical across both cases and are the query SHAs
   distinct and bound to the extracted members?
3. Do both author/RTDL gates report same-input count agreement: `1570285` and
   `242920` respectively?
4. Is the author `load_factor=1` configuration recorded, including the prior
   `0.0001` invalid-program-counter diagnostic?
5. Does each case use the generic RTDL columnar AABB prepared-count route?
6. Are author internal query time and RTDL load/prepare/query/primitive phases
   kept separate, with no ratio authorization?
7. Are relation-level, Figure 6, full-paper, author-parity, zero-copy, and
   Embree claims explicitly closed?
8. Do the local batch tests prove both artifacts match the intended bounded
   matrix without self-upgrading review status?

## Expected answer shape

```text
Verdict: approve / approve_with_required_amendments / revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
Answers 1-8: ...
Requested verdict label: ...
```
