# Call For Review: Goal5511 LibRTS Exact `select_0.001` Range-Intersects Batch

Please strictly review Goal5511 as a bounded exact-input count-evidence goal,
not as a complete paper-reproduction or performance goal.

## Files to review

- `history/internal_docs/goal5511_librts_exact_range_intersects_select0001_result_2026-07-12.md`
- `Paper-reproduction-apps/librts-paper/data/goal5511_range_intersects_select0001_exact_batch.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5511_range_intersects_batch_extraction.json`
- `Paper-reproduction-apps/librts-paper/results/goal5511_exact_range_intersects_select0001_gate.json`
- `Paper-reproduction-apps/librts-paper/results/goal5511_parks_Europe_select_0.001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5511_dtl_cnty_select_0.001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5511_USACensusBlockGroupBoundaries_select_0.001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5511_USADetailedWaterBodies_select_0.001_10000.json`
- `tests/goal5511_librts_range_intersects_select0001_test.py`
- `Paper-reproduction-apps/librts-paper/data/manifest.json`

## Review questions

1. Does the four-case manifest select the intended
   `range-intersects_select_0.001_queries_10000` members from the verified
   archive, with extraction and SHA-256 evidence?
2. Do all four independent checkpoints show equality between author and RTDL
   result counts on the same geometry and query files?
3. Does the gate preserve count-level scope because the standard author binary
   does not expose pair rows?
4. Does the RTDL route remain generic and use the public AABB columnar front
   door without adding LibRTS-specific behavior to RTDL core?
5. Are author internal query time, RTDL loading, preparation, and prepared
   query phases kept separate, with no unauthorized performance ratio?
6. Does the package avoid claiming a complete 42-pair matrix, Figure 6,
   pointwise relation equality, full-paper reproduction, zero-copy, author
   parity, or Embree evidence?
7. Is independent per-case checkpointing sufficient to avoid repeating the
   Goal5509 batch evidence-loss failure mode?
8. Is the remaining scope correctly limited to the unresolved Goal5509 large
   cases and the rest of the exact archive, rather than silently promoting
   this four-case family to a complete matrix?

## Required answer shape

```text
Verdict: <approve|approve_with_required_amendments|revise>
Blocking findings:
- <none or findings>
Required amendments:
- <none or amendments>
Non-blocking notes:
- <notes>

Answers:
1. <answer>
2. <answer>
3. <answer>
4. <answer>
5. <answer>
6. <answer>
7. <answer>
8. <answer>
```

## Forbidden conclusions

- Do not call this a complete official range-intersects matrix.
- Do not infer pairwise relation equality from count equality.
- Do not report a performance ratio from the separated phase fields.
- Do not call this Figure 6 or full-paper reproduction.
- Do not claim zero-copy, author-performance parity, native algorithm
  equivalence, or Embree evidence.
