# Batch Call For Review: Goals5485-5491 LibRTS Prepared Columnar Pipeline

Please strictly review Goals5485-5491 as one evidence packet. This batch starts
after the already independently verified Goals5482-5484 exact point-contains
count closeout. The question is whether the new prepared-phase, generic
columnar front door, app integration, repeat-regime diagnostics, numeric-loader
no-go, and hash-bound cache are technically sound and honestly bounded.

Do not review this as a Figure-6 reproduction or a performance-parity claim.
The author binary exposes counts for these cases, not point-to-polygon pair
relations. Equal counts therefore do not establish relation equality.

## Packet scope

### Goal5485: first prepared-phase gate

Exact `dtl_cnty` official archive members are passed to the author and RTDL.
The gate separates WKT load, index preparation, prepared query wall, and RTDL
primitive query phase. It establishes count agreement only and keeps author
internal query time separate from RTDL wall time.

### Goal5486: six-case prepared-phase matrix

The same phase gate runs on six exact official geometry/query member pairs:
`dtl_cnty`, `USACensusBlockGroupBoundaries`, `USADetailedWaterBodies`,
`parks_Europe`, `lakes.bz2`, and `parks.bz2`. All six counts match. The largest
cases show that WKT ingestion dominates the app route while the prepared
query phase is sub-second.

### Goal5487: generic RTDL columnar front door

RTDL adds public app-neutral `Aabb2DColumns` and
`prepare_aabb_index_2d_columns`. A tiny POD gate compares it with the existing
row-shaped OptiX front door and gets identical point-contains counts. The
implementation is a host ABI/packing path; it does not claim device zero-copy.

### Goal5488: LibRTS app integration

The LibRTS app-owned WKT loader emits `Aabb2DColumns` and uses the new public
front door on exact `dtl_cnty` and `lakes.bz2`. Counts and input hashes match.
On `lakes.bz2`, the earlier row/ctypes prepare phase was about `66.311s` and
the columnar prepare phase about `0.856s`, while WKT loading remained about
`405s`. The single-run query phase was explicitly not used for a ratio.

### Goal5489: same-process repeat matrix

One prepared columnar index is queried three times in the same process on
exact `dtl_cnty` and `lakes.bz2`. All counts match. The measured route walls
are:

```text
dtl_cnty: 0.369s, 0.220s, 0.218s
lakes:    0.598s, 0.222s, 0.220s
```

The primitive phases are:

```text
dtl_cnty: 0.202s, 0.070s, 0.069s
lakes:    0.447s, 0.072s, 0.072s
```

This is a same-process first-use/reuse diagnostic, not a distinct-query
query-many result, fresh-process distribution, author ratio, or end-to-end
speedup.

### Goal5490: numeric WKT loader no-go

An app-owned NumPy `fromstring` WKT numeric parser is compared on exact
`dtl_cnty`. It preserves all columns and count agreement, but load is
`28.069s` versus `27.994s` in a separate Goal5489 run. No material benefit is
demonstrated, so the variant remains experimental and is not run on the
6.7GB lakes input merely to search for a favorable number.

### Goal5491: reusable exact AABB column cache

The app builds an atomic `.npz`/JSON cache from exact WKT-derived AABB columns.
The metadata binds source path/name/size/SHA-256, row count, dtype, and schema;
load rejects stale source hashes. On exact `lakes.bz2`, the cache contains
`8,327,448` rows and is `286MB`. Cache load plus source hash validation is
`8.101s`, index preparation `0.840s`, and three queries match author count
`103189` with query walls `0.350s`, `0.216s`, `0.218s`.

The original WKT parse was `406.570s`; cache construction is a separate
one-time phase and must remain visible. This is reusable-ingestion evidence,
not an end-to-end performance ratio.

## Files to inspect

Reports:

```text
history/internal_docs/goal5485_librts_exact_point_contains_prepared_phase_gate_result_2026-07-11.md
history/internal_docs/goal5486_librts_exact_point_contains_prepared_phase_matrix_result_2026-07-11.md
history/internal_docs/goal5487_generic_aabb_columnar_frontdoor_result_2026-07-11.md
history/internal_docs/goal5488_librts_prepared_phase_columnar_loader_result_2026-07-12.md
history/internal_docs/goal5489_librts_prepared_phase_repeat_result_2026-07-12.md
history/internal_docs/goal5490_librts_numeric_wkt_loader_no_go_result_2026-07-12.md
history/internal_docs/goal5491_librts_exact_aabb_column_cache_result_2026-07-12.md
```

Implementations and tests:

```text
src/rtdsl/aabb_columns.py
src/rtdsl/aabb_index.py
src/rtdsl/optix_runtime.py
Paper-reproduction-apps/librts-paper/run_exact_point_contains_count_gate.py
Paper-reproduction-apps/librts-paper/run_exact_point_contains_prepared_phase_columns_repeat.py
Paper-reproduction-apps/librts-paper/build_exact_aabb_column_cache.py
tests/goal5487_generic_aabb_columnar_frontdoor_test.py
tests/goal5488_librts_prepared_phase_columnar_gate_test.py
tests/goal5489_librts_prepared_phase_repeat_test.py
```

Machine-readable evidence:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5485_dtl_cnty_prepared_phase.json
Paper-reproduction-apps/librts-paper/results/librts_goal5486_prepared_phase_batch.json
Paper-reproduction-apps/librts-paper/results/librts_goal5487_generic_aabb_columnar_pod_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5488_dtl_cnty_prepared_phase_columns.json
Paper-reproduction-apps/librts-paper/results/librts_goal5488_lakes_bz2_prepared_phase_columns.json
Paper-reproduction-apps/librts-paper/results/librts_goal5489_dtl_cnty_repeat.json
Paper-reproduction-apps/librts-paper/results/librts_goal5489_lakes_bz2_repeat.json
Paper-reproduction-apps/librts-paper/results/librts_goal5490_dtl_cnty_numeric_loader.json
Paper-reproduction-apps/librts-paper/results/librts_goal5491_lakes_cache_build.json
Paper-reproduction-apps/librts-paper/results/librts_goal5491_lakes_bz2_cache_repeat.json
```

## Cross-cutting review questions

1. Are the exact archive/member provenance and geometry/query SHA-256 checks
   sufficient for every claimed exact-input case?
2. Does Goal5486 truly preserve count-level scope and avoid implying
   pointwise containment relation equality?
3. Is `Aabb2DColumns` app-neutral, correctly validated, and safely handed to
   the native ABI with owner/lifetime guarantees?
4. Does Goal5487 prove a generic system capability rather than a LibRTS-only
   path, and is the no-device-zero-copy wording accurate?
5. Are Goal5488's `66.311s -> 0.856s` phase numbers correctly framed as host
   packing evidence rather than an end-to-end speedup?
6. Does Goal5489 correctly separate first-use, subsequent same-process query,
   primitive phase, WKT load, and index preparation?
7. Is the Goal5490 numeric-loader no-go justified by the evidence, and is it
   correct not to spend the large lakes run on an unsupported hypothesis?
8. Does Goal5491's cache publication remain atomic and fail closed on stale,
   incomplete, or mismatched source metadata?
9. Is reusing the exact-input author result for Goal5491 legitimate after hash
   validation, and is that reuse clearly distinguished from rerunning author?
10. Are one-time cache build, cache storage, cache load, RTDL preparation,
    query wall, and primitive query phases all visible and non-mixed?
11. Do all core changes remain generic, with WKT parsing/cache lifecycle and
    paper-specific comparison owned by the LibRTS app?
12. Are the following claims correctly forbidden throughout the packet:
    author performance ratio/parity, end-to-end speedup, pointwise relation
    equivalence, Figure 6 reproduction, full paper reproduction, device
    zero-copy, and Embree evidence?
13. Does the batch have enough local tests, POD evidence, manifest entries,
    and memory updates to close the implemented goals while leaving their
    external-review status explicit?

## Required output

Please provide one verdict per goal and one batch verdict:

```text
Goal5485: approve | revise
Goal5486: approve | revise
Goal5487: approve | revise
Goal5488: approve | revise
Goal5489: approve | revise
Goal5490: approve_no_go | revise
Goal5491: approve | revise

Batch verdict: approve | approve_with_required_amendments | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
Claim boundary confirmation: ...
```
