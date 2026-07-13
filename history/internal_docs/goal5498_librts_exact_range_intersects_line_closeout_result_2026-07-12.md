# Goal5498 LibRTS Exact Range-Intersects Line Closeout

## Status

```text
bounded_exact_range_intersects_two_case_line_closed__remaining_pairs_queued__review_pending
```

## Closed evidence

- Goal5492 inventory: `42` exact range-intersects pairs in the verified
  official archive.
- Goal5496: exact `dtl_cnty` `select_0.01 / 10,000` count matched at
  `1,570,285`.
- Goal5497: exact `dtl_cnty` `select_0.0001 / 10,000` count matched at
  `242,920`.
- Both cases use the generic RTDL columnar prepared AABB path and the same
  exact geometry SHA with distinct query SHA values.

The current bounded line is closed after two exact query cases. The remaining
`40` exact archive pairs stay queued for a separately scoped batch; they are
not silently treated as executed.

## Configuration note

The author `load_factor=0.0001` configuration produced a CUDA invalid-program-
counter failure on the first exact range-intersects case. The same inputs and
operation succeeded with `load_factor=1`, which is explicitly recorded in both
gate artifacts. This is an execution configuration fact, not a performance
claim.

## Claim boundary

This closes only a bounded exact-input **count** line. It does not establish
pointwise intersection relation equality, complete range-intersects coverage,
Figure 6 reproduction, author performance parity, full paper reproduction,
device zero-copy, or Embree evidence. PIP and mutation remain blocked by the
verified archive inventory's lack of exact pairs. Goal5498 is implemented and
external-review pending.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5497_range_intersects_dtl_cnty_select0001_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5497_range_intersects_dtl_cnty_select0001_extraction.json
```
