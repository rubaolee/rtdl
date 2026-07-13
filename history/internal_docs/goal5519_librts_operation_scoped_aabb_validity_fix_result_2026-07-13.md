# Goal5519 LibRTS Operation-Scoped AABB Validity Fix

Status: `implemented__exact_lakes_range_contains_match_restored__review_pending`

## Objective

Resolve the exact official `lakes.bz2 range-contains_queries_100000` count
disagreement without adding LibRTS identity or paper-specific behavior to RTDL.

## Observed regression

The same exact archive geometry and query files produced:

```text
author RTSpatial: 101,418
RTDL after Goal5508: 101,339
delta: 79
```

The geometry SHA-256 is
`0cde2245faf03cb0cf48cf9f8ffb0e31a7391300d947fa9de2110a46006e2f03`;
the query SHA-256 is
`f4119e7d429ab8cd9355f0b1ef1f3594e28fb6b6e1ce70fcdaff1a557c13c3b8`.

## Diagnosis

The app-owned exact AABB cache contains 8,327,448 indexed rows. After float32
packing, 276 are not strict; 215 were valid in float64 but collapsed in
float32. Only two collapsed rows have nonzero inclusive range-containment
contributions, and their counts are `21 + 58 = 79`.

An A/B run with the same cached columns and queries isolates the regression:

```text
pre-Goal5508 native build: 101,418
Goal5508 strict guard build: 101,339
```

The author source is operation-specific too. At pinned RTSpatial commit
`7c54c181b1058c87768767998c00e225cc58666e`, the envelope-contains shader calls
`envelope.Contains(query)` without an `IsValid()` guard, while the envelope
intersection shader checks `geom.IsValid()`.

A two-row synthetic author subset returns zero and is retained as a negative
control: it prevents this report from claiming that the subset alone proves
the full author result. The full-input native A/B, source audit, and exact
delta decomposition together establish the RTDL regression.

## Generic fix

The OptiX strict indexed-box validity guard is now scoped to `range_intersects`.
`point_contains` and `range_contains` use their inclusive exact predicates
after numeric packing. This is an operation contract, not a LibRTS branch.

The discriminating hardware fixture now produces:

```text
point_contains:   1
range_contains:   1
range_intersects: 0
```

for a box that has positive area in float64 and collapses in one dimension in
float32.

## POD verification

The writable build tree was moved to `/tmp/rtdl-goal5519` after the POD's
`/workspace` user quota rejected source writes. Local and POD source SHA-256
values were verified before building. The rebuilt library SHA-256 is
`75e7d0dea9f10e98e179c2617a3401f872ca09de0a54adbb57792cb8675120df`.

Results:

```text
exact lakes range_contains:      101,418 == author 101,418
lakes range_intersects prefix: 34,581,812 == prior/author 34,581,812
degenerate range_intersects:             0 == expected 0
```

Eleven focused local tests pass.

## Claim boundary

This goal proves one exact count correction and a generic operation-scoped
native semantic fix. It does not prove pointwise containment relations, the
complete 14-pair range-contains matrix, Figure 6, performance parity, full
paper reproduction, author algorithm equivalence, zero-copy, or Embree.

Primary evidence:

```text
Paper-reproduction-apps/librts-paper/results/goal5519_operation_scoped_aabb_validity_fix_gate.json
```
