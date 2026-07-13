# Goal5497 LibRTS Exact Range-Intersects Batch Extension

## Status

```text
exact_input_range_intersects_two_case_batch_matched__review_pending
```

## Result

Goal5497 adds a second exact range-intersects query member for the same
verified `dtl_cnty` geometry. Together with Goal5496, the two cases are:

```text
query member                                      author       RTDL
range-intersects_select_0.01_queries_10000        1570285      1570285
range-intersects_select_0.0001_queries_10000       242920       242920
```

The geometry SHA-256 is identical in both cases:

```text
9177fdff45f24488f22157a2a1428a7cdb9d5a66a7287d4013ead52de1c7973f
```

The query SHA-256 values are distinct and recorded in the per-case gate
artifacts. Both cases use the pinned author binary with explicit
`load_factor=1`; the earlier `0.0001` configuration failed on the first case
with a CUDA invalid-program-counter error and is not hidden.

## Phase evidence

Goal5497's RTDL phases are WKT/column load `28.003s`, index preparation
`0.365s`, prepared query wall `0.636s`, and primitive query phase `0.602s`.
Goal5496 records its own phases separately. The author's internal query time
is not the same denominator as RTDL route wall, so no performance ratio is
computed.

## Claim boundary

This is a two-case exact-input same-input **count** matrix. It does not
establish pointwise intersection relation equality, Figure 6 reproduction,
author performance parity, full paper reproduction, device zero-copy, or
Embree evidence. Goal5497 is implemented and external-review pending.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5497_range_intersects_dtl_cnty_select0001_extraction.json
Paper-reproduction-apps/librts-paper/results/librts_goal5497_range_intersects_dtl_cnty_select0001_gate.json
```
