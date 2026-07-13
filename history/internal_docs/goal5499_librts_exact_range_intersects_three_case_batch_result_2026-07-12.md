# Goal5499 LibRTS Exact Range-Intersects Three-Case Batch

## Status

```text
exact_input_range_intersects_three_case_batch_matched__review_pending
```

Goal5499 adds a third exact query member for the same verified `dtl_cnty`
geometry. The current three-case matrix is:

```text
query member                                      author       RTDL
range-intersects_select_0.01_queries_10000        1570285      1570285
range-intersects_select_0.0001_queries_10000       242920       242920
range-intersects_select_0.001_queries_10000        239884       239884
```

All three cases use geometry SHA
`9177fdff45f24488f22157a2a1428a7cdb9d5a66a7287d4013ead52de1c7973f`; each query
member has its own recorded SHA-256. The author uses explicit `load_factor=1`.
The prior `0.0001` configuration failure remains recorded in Goals5496-5498.

Goal5499 RTDL phases are WKT/column load `28.013s`, index preparation
`0.420s`, prepared query wall `0.192s`, and primitive query phase `0.158s`.
Author internal query time is a different denominator; no ratio is computed.

## Claim boundary

This is a three-case exact-input same-input **count** matrix for one geometry.
It does not establish complete range-intersects coverage, pointwise relation
equality, Figure 6 reproduction, author performance parity, full paper
reproduction, device zero-copy, or Embree evidence. Goal5499 is implemented
and external-review pending.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5497_range_intersects_dtl_cnty_select0001_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5499_range_intersects_dtl_cnty_select0001_extraction.json
Paper-reproduction-apps/librts-paper/results/librts_goal5499_range_intersects_dtl_cnty_select0001_gate.json
```
