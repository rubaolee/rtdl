# Goal5496 LibRTS Exact Range-Intersects Count Gate

## Status

```text
exact_input_range_intersects_count_matched__review_pending
```

## Input

Goal5492 identified this pair in the verified official archive:

```text
geometry: PPoPPAE/datasets/polygons/dtl_cnty.wkt
query:    PPoPPAE/datasets/queries/range-intersects_select_0.01_queries_10000/dtl_cnty.wkt
```

The geometry is the same verified archive member reused by Goal5493. The final
gate revalidated its SHA-256 and recorded the query SHA-256:

```text
geometry: 9177fdff45f24488f22157a2a1428a7cdb9d5a66a7287d4013ead52de1c7973f
query:    f901553c4d9a25f1df567051f5a1f940723d46a7c74e25a02339eb25f185dce7
```

Both files were passed unchanged to the pinned author binary and the RTDL
route. The author-only `load_factor=0.0001` probe failed with CUDA
`invalid program counter`; the same exact inputs and `range-intersects`
operation succeeded with `load_factor=1`. The final gate records that setting
explicitly. This is an author execution configuration, not a performance
claim.

## Result

```text
author result count: 1570285
rtdl result count:   1570285
matched:             true
geometry count:      12234
query count:         10000
```

RTDL used the generic
`Aabb2DColumns -> prepare_aabb_index_2d_columns -> prepared.count` route with
OptiX acceleration. The recorded RTDL phases were WKT/column load `27.842s`,
index preparation `0.446s`, prepared query wall `0.660s`, and primitive query
phase `0.627s`. The author reported internal query time `0.7824ms`; this is a
different denominator and no ratio is computed.

## Claim boundary

This is exact-input same-input **count** agreement only. It does not establish
pointwise intersection relation equality, Figure 6 reproduction, author
performance parity, full paper reproduction, device zero-copy, or Embree
evidence. Goals5492-5496 remain implemented/review pending until external
review; no status is self-upgraded.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_extraction.json
Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_gate.json
```
