# Goal5493 LibRTS Exact Range-Contains Count Gate

## Status

```text
exact_input_range_contains_count_matched__review_pending
```

## Input

The exact official archive supplied:

```text
geometry: PPoPPAE/datasets/polygons/dtl_cnty.wkt
query:    PPoPPAE/datasets/queries/range-contains_queries_100000/dtl_cnty.wkt
```

The selected subset was published atomically and recorded SHA-256 values:

```text
geometry: 9177fdff45f24488f22157a2a1428a7cdb9d5a66a7287d4013ead52de1c7973f
query:    b6b388481f3c27a14adacb36e6a4acfbe56a2c0cd012dcf853e753eed3adb9a4
```

## Result

```text
author result count: 117314
rtdl result count:   117314
matched:             true
geometry count:      12234
query count:         100000
```

RTDL used the generic `Aabb2DColumns -> prepare_aabb_index_2d_columns ->
prepared.count(operation="range_contains")` route with OptiX acceleration.
Measured RTDL phases were WKT/column load `29.074s`, index preparation
`0.374s`, prepared query wall `0.865s`, and primitive query phase `0.633s`.
The author reported internal query time `0.0844ms`; this is a different
denominator and no ratio is computed.

## Claim boundary

This is exact-input same-input **count** agreement only. It does not establish
pointwise relation equality, range Figure reproduction, author parity, full
paper reproduction, device zero-copy, or Embree evidence.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5493_range_contains_dtl_extraction.json
Paper-reproduction-apps/librts-paper/results/librts_goal5493_range_contains_dtl_gate.json
```
