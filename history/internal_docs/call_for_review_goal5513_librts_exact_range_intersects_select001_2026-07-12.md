# Call For Review: Goal5513 LibRTS Exact `select_0.01` Range-Intersects Batch

Please strictly review Goal5513 as bounded exact-input count evidence, not as
a complete paper-reproduction or performance result.

## Files to review

- `history/internal_docs/goal5513_librts_exact_range_intersects_select001_result_2026-07-12.md`
- `Paper-reproduction-apps/librts-paper/data/goal5513_range_intersects_select001_exact_batch.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5513_range_intersects_batch_extraction.json`
- `Paper-reproduction-apps/librts-paper/results/goal5513_exact_range_intersects_select001_gate.json`
- `Paper-reproduction-apps/librts-paper/results/goal5513_parks_Europe_select_0.01_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5513_dtl_cnty_select_0.01_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5513_USACensusBlockGroupBoundaries_select_0.01_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5513_USADetailedWaterBodies_select_0.01_10000.json`
- `tests/goal5513_librts_range_intersects_select001_test.py`
- `Paper-reproduction-apps/librts-paper/data/manifest.json`

## Review questions

1. Are the four query members exact archive members with valid SHA-256
   provenance and the intended `.01` query family?
2. Do all four independent checkpoints show same-input author/RTDL count
   equality?
3. Is the parks workspace output-stream retry disclosed as an environment
   workaround rather than a semantic or performance change?
4. Does the route remain generic and use the public AABB columnar front door?
5. Are author and RTDL timing phases kept separate with no ratio claim?
6. Does the package remain count-level because the standard author binary does
   not expose pair rows?
7. Does it avoid complete-matrix, Figure 6, full-paper, zero-copy,
   author-parity, and Embree claims?
8. Is the remaining archive coverage correctly left as separate work?

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

- Do not call this a complete official matrix or Figure 6 reproduction.
- Do not infer pairwise relation equality from count equality.
- Do not report a performance ratio from these phase fields.
- Do not claim full-paper reproduction, zero-copy, author parity, native
  algorithm equivalence, or Embree evidence.
