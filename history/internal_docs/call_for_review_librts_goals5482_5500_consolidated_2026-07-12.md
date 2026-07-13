# Consolidated Call For Review: LibRTS Goals5482-5500

Please perform one strict, evidence-first review of the LibRTS paper-app
workstream through Goal5500. The review should treat Goals5482-5491 as the
previously reviewed baseline and focus the new external decision on
Goals5492-5500, without silently reopening or upgrading any prior status.

This is a consolidated review request, not a request to approve every result.
In particular, Goal5500 is a deliberately partial six-geometry batch:
three count matches, two same-input count disagreements, and one author-side
CUDA allocation failure. Do not turn that into a six-case success headline.

## Review Scope And Status

### Previously reviewed baseline

```text
Goals5482-5484: exact Figure-6 point-contains count closeout;
                externally reviewed and approved.
Goals5485-5491: prepared columnar AABB phase/cache line;
                externally reviewed and approved, with Goal5490 a no-go.
```

The baseline established:

- official archive MD5 and selected-member SHA-256 provenance;
- same-input author/RTDL count gates;
- generic `Aabb2DColumns` and `prepare_aabb_index_2d_columns` usage;
- app-owned cache and phase separation;
- no author ratio, paper-performance, Figure-6 completion, zero-copy, or
  Embree claim.

### Current review-pending line

```text
Goal5492: exact archive operation inventory
Goal5493: exact range-contains selected pair
Goal5494: cache lifecycle remains app-owned
Goal5495: point/range-contains line closeout and range-intersects continuation
Goal5496: first exact range-intersects count gate
Goal5497: second exact range-intersects query case
Goal5498: bounded two-case line closeout
Goal5499: third exact range-intersects query case
Goal5500: six-geometry exact range-intersects batch attempt
```

All nine are implemented and review pending. No status is self-upgraded by
this packet.

## Files To Review

### Current reports and calls

```text
history/internal_docs/goal5492_librts_exact_archive_operation_inventory_result_2026-07-12.md
history/internal_docs/goal5493_librts_exact_range_contains_dtl_result_2026-07-12.md
history/internal_docs/goal5494_librts_cache_lifecycle_system_api_decision_result_2026-07-12.md
history/internal_docs/goal5495_librts_point_contains_range_contains_current_line_closeout_result_2026-07-12.md
history/internal_docs/goal5496_librts_exact_range_intersects_dtl_result_2026-07-12.md
history/internal_docs/goal5497_librts_exact_range_intersects_batch_result_2026-07-12.md
history/internal_docs/goal5498_librts_exact_range_intersects_line_closeout_result_2026-07-12.md
history/internal_docs/goal5499_librts_exact_range_intersects_three_case_batch_result_2026-07-12.md
history/internal_docs/goal5500_librts_exact_range_intersects_six_geometry_batch_result_2026-07-12.md
```

```text
Paper-reproduction-apps/librts-paper/data/manifest.json
Paper-reproduction-apps/librts-paper/data/goal5500_range_intersects_representative_cases.json
Paper-reproduction-apps/librts-paper/extract_verified_operation_batch.py
Paper-reproduction-apps/librts-paper/run_exact_range_intersects_batch.py
Paper-reproduction-apps/librts-paper/results/librts_goal5492_exact_archive_operation_inventory.json
Paper-reproduction-apps/librts-paper/results/librts_goal5493_range_contains_dtl_extraction.json
Paper-reproduction-apps/librts-paper/results/librts_goal5493_range_contains_dtl_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5497_range_intersects_dtl_cnty_select0001_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5499_range_intersects_dtl_cnty_select0001_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5500_range_intersects_batch_extraction.json
Paper-reproduction-apps/librts-paper/results/librts_goal5500_range_intersects_batch_gate.json
```

```text
tests/goal5492_librts_exact_archive_operation_inventory_test.py
tests/goal5493_librts_verified_operation_subset_test.py
tests/goal5493_librts_exact_range_contains_count_gate_test.py
tests/goal5496_librts_exact_range_intersects_count_gate_test.py
tests/goal5497_librts_exact_range_intersects_batch_evidence_test.py
tests/goal5498_librts_exact_range_intersects_line_closeout_test.py
tests/goal5499_librts_exact_range_intersects_three_case_batch_test.py
tests/goal5500_librts_exact_range_intersects_batch_tools_test.py
tests/goal5500_librts_exact_range_intersects_batch_result_test.py
```

### Baseline evidence to cross-check, not silently re-review

```text
history/internal_docs/review_goals5482_5484_librts_exact_point_contains_closeout_verified_2026-07-11.md
history/internal_docs/review_goals5485_5491_librts_prepared_columnar_batch_2026-07-12.md
Paper-reproduction-apps/librts-paper/results/librts_goal5479_pod_download_verified.json
Paper-reproduction-apps/librts-paper/results/librts_goal5486_prepared_phase_batch.json
Paper-reproduction-apps/librts-paper/results/librts_goal5487_generic_aabb_columnar_pod_gate.json
Paper-reproduction-apps/librts-paper/results/librts_goal5491_lakes_bz2_cache_repeat.json
```

## Evidence Summary To Verify

### Exact archive inventory and selected operations

The official `PPoPPAE-v2.tar.gz` archive is bound to:

```text
MD5: 89e589f086038f1cd3af9e3ed67da8c8
published size: 23,062,425,365 bytes
```

Goal5492 inventories:

```text
exact point-contains pairs: 14
exact range-contains pairs: 14
exact range-intersects pairs: 42
exact PIP pairs: 0
exact mutation pairs: 0
```

The review must check that later selected-member extraction remains bound to
this verified archive, exact member paths, sizes, and SHA-256 values.

### Exact range-contains

Goal5493 runs the exact `dtl_cnty` range-contains member and matches author and
RTDL count `117,314` on the same files. The result is count-level evidence;
there is no relation-level or performance claim.

### Exact range-intersects single-geometry line

Goals5496-5499 run three exact query members for the same `dtl_cnty` geometry:

```text
select 0.01   -> 1,570,285 author = RTDL
select 0.0001 ->   242,920 author = RTDL
select 0.001  ->   239,884 author = RTDL
```

The author gate uses `load_factor=1`. The prior `load_factor=0.0001` attempt
failed with a CUDA invalid-program-counter error on the POD and remains visible
as a diagnostic, not a silently replaced result.

### Goal5500 six-geometry batch

The same official query family was attempted for six geometries:

| Geometry | Author | RTDL | Outcome |
|---|---:|---:|---|
| `parks_Europe` | 216,977,211 | 216,981,002 | count disagreement, RTDL +3,791 |
| `parks.bz2` | CUDA OOM | not run | author allocation failure |
| `dtl_cnty` | 1,570,285 | 1,570,285 | matched |
| `lakes.bz2` | 1,113,229,623 | 1,113,284,318 | count disagreement, RTDL +54,695 |
| `USACensusBlockGroupBoundaries` | 33,404,355 | 33,404,355 | matched |
| `USADetailedWaterBodies` | 55,205,607 | 55,205,607 | matched |

The correct interpretation is:

```text
6 exact pairs attempted
3 count matches
2 count disagreements requiring diagnosis
1 author CUDA allocation failure
```

The two disagreements are not called semantic bugs because the standard
author binary emits counts rather than pair rows. The likely investigation
space includes float32 conversion, AABB padding, diagonal intersection
semantics, or another author/RTDL contract difference, but no root cause is
authorized yet.

## Cross-Cutting Architecture Questions

1. Does the LibRTS app use RTDL's generic AABB/columnar APIs rather than
   introducing LibRTS-specific primitives into `src/rtdsl` or `src/native`?
2. Is the app-owned WKT parsing, archive extraction, author parser, cache,
   comparator, and tolerance policy kept outside RTDL core?
3. Does the cache decision correctly remain app-owned because no second generic
   consumer and no generic lifecycle contract have yet been established?
4. Does the batch extractor safely reuse one verified archive and avoid full
   archive expansion on the quota-limited POD?
5. Does the batch runner create per-case serialization directories, pass the
   verified archive evidence, and record failures rather than dropping cases?
6. Are exact-input identity, count equality, relation equality, phase timing,
   and performance comparison kept as separate claims?
7. Is the author `load_factor=1` choice visible and reproducible, with the
   prior failing configuration preserved as a diagnostic?
8. Is the `parks.bz2` OOM correctly classified as author-side capacity failure,
   not semantic mismatch and not RTDL success?
9. Does the next step correctly prioritize mismatch diagnosis over more route
   tuning or cache promotion?
10. Does the complete packet preserve the project rule that Embree is out of
    scope for this campaign?

## Performance And Phase Review

The packet contains phase diagnostics only. Author internal query time excludes
loading; RTDL records WKT/column loading, index preparation, prepared-query
wall, and primitive query phases. These are different denominators and
execution models. Review must verify that:

- no author-vs-RTDL ratio is reported;
- no prepared-query time is presented as end-to-end performance;
- no cache reuse is presented as paper speedup;
- large WKT ingestion remains visible as a major RTDL engineering cost;
- no performance parity, full-paper, Figure 6, or Embree claim is inferred.

## Required Claim Boundary

The reviewer must reject any summary that says:

```text
six exact range-intersects cases matched
full range-intersects matrix complete
RTDL and author relation rows are equal
RTDL is faster than the author
author performance parity
Figure 6 reproduced
full LibRTS paper reproduction
parks.bz2 semantic mismatch
Embree comparison
```

The strongest authorized current summary is:

```text
The LibRTS app has exact archive provenance and a generic columnar AABB route.
Across Goals5492-5500, three exact range-intersects cases match author counts;
two larger cases disagree in count and require diagnosis; one author case is
blocked by CUDA allocation failure. No relation-level, complete-matrix,
performance-ratio, figure, full-paper, zero-copy, or Embree claim is closed.
```

## Review Deliverable

Please return one consolidated verdict in this shape:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Goal5492-5500 status decisions:
Answers to cross-cutting questions 1-10:
Claim boundary decision:
Next-goal decision:
Requested verdict label:
```

The most important decision is not whether the partial batch looks promising;
it is whether the evidence and boundaries are honest enough to close the
current batch line, or whether the two count disagreements require a new
diagnostic goal before any broader LibRTS claim is accepted.
