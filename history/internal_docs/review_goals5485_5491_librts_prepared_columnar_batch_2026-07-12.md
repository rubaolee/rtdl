# External Review: Goals5485-5491 LibRTS Prepared Columnar Pipeline

## Verdict

```text
Goal5485: approve
Goal5486: approve
Goal5487: approve
Goal5488: approve
Goal5489: approve
Goal5490: approve_no_go
Goal5491: approve

Batch verdict: approve
```

Blocking findings: none.

Required amendments: none.

## Review scope

This review covers the prepared-phase gate, six-case exact-input matrix,
generic `Aabb2DColumns` front door, LibRTS integration, same-process repeat
diagnostics, numeric WKT loader no-go, and hash-bound exact AABB cache. It does
not approve Figure 6 reproduction, pointwise containment equivalence, author
performance parity, an end-to-end speedup, device zero-copy, full paper
reproduction, or Embree evidence.

## Findings by goal

### Goal5485

Approved. The exact `dtl_cnty` gate separates WKT load, index preparation,
prepared query wall, and RTDL primitive query time. The author and RTDL count
match is count-level only, with author internal query time kept separate.

### Goal5486

Approved. Six exact official geometry/query member pairs all match by result
count. The matrix keeps WKT loading visible and does not turn prepared-phase
measurements into an author ratio.

### Goal5487

Approved. `Aabb2DColumns` and `prepare_aabb_index_2d_columns` are genuinely
app-neutral, exported, and consumed by a non-app synthetic CPU reference test.
Owner/lifetime handling and native ABI packing validation are present. The
structured buffer is a host ABI view; the `device_zero_copy_claimed` flag is
correctly false.

### Goal5488

Approved. The LibRTS app emits the generic column contract and preserves exact
input hashes and count agreement on `dtl_cnty` and `lakes.bz2`. The
`66.311s -> 0.856s` number is correctly framed as a prepare-phase host
packing change, not an end-to-end result; WKT load around `405s` remains
visible and dominant.

### Goal5489

Approved. One prepared index is queried three times on each of `dtl_cnty` and
`lakes.bz2`. First-use and subsequent same-process query phases are separated.
This is a reuse diagnostic, not a distinct-query query-many result, fresh
process distribution, performance ratio, or end-to-end speedup.

### Goal5490

Approved as a no-go. The experimental NumPy numeric WKT loader preserves the
column values and exact count, but `28.069s` versus the separate `27.994s`
baseline demonstrates no material benefit. It was correctly not run on the
6.7GB lakes input merely to search for a favorable number.

### Goal5491

Approved. The app-owned `.npz`/JSON cache is published atomically and binds
source size, SHA-256, row count, dtype, and schema. Loading fail-closes on
stale source hash, incomplete cache pair, bad schema, or row-count mismatch.
The exact lakes cache contains `8,327,448` rows and is `286MB`; cache load plus
source validation is `8.101s`, preparation `0.840s`, and all three queries
match author count `103189`. Reused author evidence is legitimate because the
runner revalidates the geometry/query hashes and labels the run as reuse
diagnostic.

## Cross-cutting confirmation

- Exact geometry/query SHA-256 provenance is preserved.
- Count equality is not presented as pointwise relation equality.
- RTDL core remains generic; WKT parsing, cache lifecycle, and paper comparison
  remain app-owned.
- `performance_ratio_authorized`, `device_zero_copy_claimed`,
  `pointwise_containment_equivalence_claimed`, and `figure6_reproduced` remain
  false in the evidence.
- One-time cache build, cache storage, cache load, RTDL preparation, query wall,
  and primitive phases remain distinct.
- The review-pending status was not silently upgraded by implementation; this
  file is the external approval record that authorizes the status transition.

## Non-blocking notes

1. The prepare-phase improvement does not materially change end-to-end time
   while WKT loading dominates.
2. RTDL prepared query wall remains far above the author's internal query time;
   keeping the ratio unauthorized is correct.
3. Cache construction remains a one-time cost and must stay visible in future
   summaries.

## Review basis

The review checked the actual source files, tests, manifest, and nine
machine-readable evidence artifacts. The POD/native test suite was not rerun
during this review because of shell instability; the existing POD artifacts and
source-level fail-closed checks were used.
