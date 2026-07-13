# Call For Review: Goals 5482-5483

Please strictly review the Goals5482-5483 LibRTS exact Figure-6
point-contains extension against the actual source and evidence files.

## Files to inspect

- `Paper-reproduction-apps/librts-paper/run_exact_point_contains_batch_gate.py`
- `Paper-reproduction-apps/librts-paper/run_exact_point_contains_count_only_gate.py`
- `tests/goal5482_librts_exact_point_contains_batch_gate_test.py`
- `tests/goal5483_librts_exact_point_contains_count_only_gate_test.py`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5482_point_contains_remaining_subset.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5482_exact_point_contains_remaining_batch.json`
- `Paper-reproduction-apps/librts-paper/results/goal5482_point_contains/*.json`
- `Paper-reproduction-apps/librts-paper/data/manifest.json`
- `history/internal_docs/goal5482_5483_librts_exact_figure6_point_contains_matrix_result_2026-07-11.md`

## Review questions

1. Is the archive provenance bound to the verified 23,062,425,365-byte,
   MD5-verified PPoPP AE archive rather than an unverified local copy?
2. Does the subset evidence identify all ten selected members with relative
   paths, sizes, and SHA-256 values, and does the runner revalidate them before
   execution?
3. Are the five new geometry/query pairs the remaining intended Figure-6
   point-contains members rather than renamed or representative substitutes?
4. Do the five result JSONs show the same exact integer count from author and
   RTDL for every case?
5. Does the aggregate evidence correctly include five new cases while keeping
   Goal5481's `dtl_cnty` case separate and visible as the sixth case?
6. Does Goal5483 use the existing generic public
   `query_aabb_index_2d(operation="point_contains")` API without introducing a
   LibRTS-specific core primitive?
7. Does the count-only route avoid requesting or materializing pair rows, and
   is the large `parks.bz2` route evidence consistent with that contract?
8. Are the input identity, result-count, backend, and claim-boundary fields
   sufficient to prevent a count match from being misread as pair-row or
   algorithmic equivalence?
9. Are Figure 6 reproduction, performance ratio, complete-paper reproduction,
   native author equivalence, and Embree correctly left unauthorized?
10. Do the local tests exercise tamper rejection, case membership, public API
    selection, and the no-row-materialization rule rather than merely scanning
    source text?
11. Does the README, results README, data manifest, and result report all carry
    the same six-of-six count-matrix boundary without stale contradictory status?
12. What, if anything, must be amended before Goals5482-5483 can be marked
    externally reviewed and approved?

## Expected answer shape

Please return:

```text
Verdict: approve | approve_with_required_amendments | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
Answers 1-12: ...
```

Do not approve a Figure-6 or performance claim merely because all six counts
match. The requested review is for exact-input count correctness and generic
API discipline only.
