# Consolidated Call For Review: Goals 5482-5484

Please strictly review the LibRTS exact Figure-6 point-contains closeout as
one package. The package contains five newly executed exact archive gates, a
count-only public-API correction for the largest input, and a denominator
audit against the author paper-branch logs.

## Scope

The authorized claim is:

```text
six exact official archive geometry/query pairs produce identical integer
point-contains counts in the author query binary and RTDL OptiX
```

The package does not claim Figure-6 reproduction, pair-row equality, a
performance ratio, full-paper reproduction, native author algorithm
equivalence, or Embree evidence.

## Primary review files

- `history/internal_docs/goal5482_5483_librts_exact_figure6_point_contains_matrix_result_2026-07-11.md`
- `history/internal_docs/goal5484_librts_exact_figure6_point_contains_denominator_audit_result_2026-07-11.md`
- `history/internal_docs/goal5482_5484_review_amendment_response_2026-07-11.md`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5482_point_contains_remaining_subset.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5482_exact_point_contains_remaining_batch.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5484_exact_figure6_point_contains_denominator.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5481_exact_point_contains.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5472_author_paper_log_denominators.json`

## Implementation and tests

- `Paper-reproduction-apps/librts-paper/run_exact_point_contains_batch_gate.py`
- `Paper-reproduction-apps/librts-paper/run_exact_point_contains_count_only_gate.py`
- `Paper-reproduction-apps/librts-paper/audit_exact_figure6_point_contains_denominator.py`
- `tests/goal5482_librts_exact_point_contains_batch_gate_test.py`
- `tests/goal5483_librts_exact_point_contains_count_only_gate_test.py`
- `tests/goal5484_librts_exact_figure6_denominator_audit_test.py`
- `Paper-reproduction-apps/librts-paper/data/manifest.json`

## Review questions

1. Is the official archive identity and ten-member Goal5482 subset provenance
   verified by path, size, and SHA-256 before execution?
2. Do the five new POD evidence JSONs show exact author/RTDL count agreement,
   and does Goal5481 provide the sixth exact case?
3. Is the large `parks.bz2` case honestly recorded as count-only, without
   claiming pair rows that the author binary does not expose?
4. Does the package explicitly state that equal counts do not establish
   pointwise containment relation equality, and does it cross-reference the
   separate Goal5467 71,626-row relation evidence without conflating workloads?
5. Does the current batch runner use the generic public
   `query_aabb_index_2d(operation="point_contains")` route rather than a
   LibRTS-specific primitive or unnecessary row materialization?
6. Does the denominator audit select exactly Figure 6, RTSpatial,
   100K-point-contains author records and reject missing/duplicate records?
7. Do geometry count, query count, and result count align for all six cases?
8. Is author internal Query Time correctly separated from Loading Time and
   from RTDL route wall?
9. Are Figure-6 reproduction, performance ratio, complete paper, native
   author equivalence, pair-row equality, and Embree claims all closed?
10. Do tests behaviorally cover hash tampering, public count API selection,
   no-row-materialization, record mismatch rejection, and ratio closure?
11. Are README, manifest, result reports, memory, and this package consistent
   about the current six-of-six status and review-pending state?
12. What required amendments, if any, must be completed before Goals5482-5484
   are marked externally reviewed and approved?

## Expected answer shape

```text
Verdict: approve | approve_with_required_amendments | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
Answers 1-11: ...
```
