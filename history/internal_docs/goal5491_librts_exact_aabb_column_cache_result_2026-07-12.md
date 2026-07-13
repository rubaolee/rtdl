# Goal5491 LibRTS Exact AABB Column Cache

## Status

```text
implemented__POD_exact_lakes_cache_reuse_matched__review_pending
```

## Objective

Separate one-time app-owned WKT ingestion from repeated RTDL prepared-query
execution. Build a reusable NumPy column cache from an exact official WKT
member, bind it to the source file's SHA-256, and feed the cache through the
generic `Aabb2DColumns` API on later runs.

## Design

The cache is entirely LibRTS app-owned:

- `.npz` stores `uint32 ids` and `float64 min_x/min_y/max_x/max_y`;
- adjacent JSON stores schema, source path/name/size/SHA-256, row count, and
  dtype metadata;
- writing is temporary-file plus atomic rename;
- loading recomputes the source SHA-256 and rejects stale or incomplete caches;
- RTDL core receives only validated `Aabb2DColumns`, not WKT or paper semantics.

## POD evidence

Input: exact official `lakes.bz2` geometry/query files, with the same hashes as
Goal5489. The cache contains `8,327,448` rows and is `286MB` on disk. Existing
author evidence was reused only after the runner revalidated the geometry and
query SHA-256 values.

| phase | value |
|---|---:|
| cache load including source-hash validation | 8.101 s |
| index prepare from cached columns | 0.840 s |
| query 1 wall | 0.350 s |
| query 2 wall | 0.216 s |
| query 3 wall | 0.218 s |
| primitive query 1 | 0.198 s |
| primitive query 2 | 0.069 s |
| primitive query 3 | 0.069 s |

All three counts matched the reused exact-input author count `103189`.
Goal5489's WKT parse/column load for the same input was `406.570s`. The cache
build is a separate one-time cost and is deliberately not hidden inside the
`8.101s` reuse phase.

## Interpretation

This is a real reusable-ingestion result: repeated runs can avoid reparsing
6.7GB of WKT and still enter the generic system API. It is not an end-to-end
speedup claim because the one-time cache build, cache storage, filesystem
behavior, and author process wall are separate concerns. The result identifies
the right product boundary: app-owned exact-input preparation plus generic
RTDL column consumption.

## Claim boundary

Authorized:

- exact-source hash-bound cache reuse;
- count agreement on the same exact input;
- generic `Aabb2DColumns` consumption after cache load;
- separation of one-time ingestion from repeated prepared queries.

Not authorized:

- author-vs-RTDL performance ratio or parity;
- end-to-end speedup;
- pointwise containment equivalence;
- Figure 6 or full paper reproduction;
- device zero-copy;
- Embree evidence.

## Evidence

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5491_lakes_cache_build.json
Paper-reproduction-apps/librts-paper/results/librts_goal5491_lakes_bz2_cache_repeat.json
```
