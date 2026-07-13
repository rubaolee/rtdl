# Goal5520 LibRTS Parks-Europe Range-Contains Cardinality Matrix

Status: `implemented__five_exact_count_matches__review_pending`

## Objective

Resolve every exact archive range-contains query cardinality available for
`parks_Europe.wkt` while preserving same-input hashes and prepared-base
accounting.

## Result

| Query rows | Author count | RTDL count |
|---:|---:|---:|
| 50,000 | 52,245 | 52,245 |
| 100,000 | 104,426 | 104,426 |
| 200,000 | 208,918 | 208,918 |
| 400,000 | 417,968 | 417,968 |
| 800,000 | 835,864 | 835,864 |

All five query files have distinct SHA-256 values and are exact official
archive members. This is not same-input replay.

## Execution accounting

The Goal5520 POD session loads the app-owned 1,856,318-row parks_Europe AABB
cache and prepares one generic RTDL OptiX AABB index. That prepared base
consumes four new distinct query batches: 50K, 200K, 400K, and 800K. The 100K
row is the independent Goal5517 checkpoint. The final gate records these as
four runtime batches plus one prior checkpoint; it does not claim that all
five ran in the same prepared session.

WKT ingestion and cache construction remain app-owned. RTDL begins at
`Aabb2DColumns` and the prepared AABB query contract. Author and RTDL timing
denominators are not compared.

## Coverage

The exact range-contains ledger moves from five matched pairs after Goal5519
to nine matched pairs after Goal5520. Five parks.bz2 cardinality pairs remain
uncheckpointed. The full 14-pair matrix is therefore not complete.

## Claim boundary

This goal proves count-level equality for one geometry across five exact query
cardinalities. It does not prove pointwise containment relations, performance
parity, Figure 6, complete paper reproduction, author algorithm equivalence,
zero-copy, or Embree.

Primary evidence:

```text
Paper-reproduction-apps/librts-paper/results/goal5520_parks_europe_range_contains_cardinality_gate.json
```
