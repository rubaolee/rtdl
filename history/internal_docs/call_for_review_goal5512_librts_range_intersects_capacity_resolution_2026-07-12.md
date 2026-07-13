# Call For Review: Goal5512 LibRTS Large-Case Capacity Resolution

Please strictly review Goal5512 as a capacity/process-state resolution goal,
not as a complete paper-reproduction or performance goal.

## Files to review

- `history/internal_docs/goal5512_librts_range_intersects_capacity_resolution_result_2026-07-12.md`
- `Paper-reproduction-apps/librts-paper/results/goal5512_parks_bz2_select0001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5512_lakes_bz2_select0001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5512_range_intersects_capacity_resolution_gate.json`
- `Paper-reproduction-apps/librts-paper/results/goal5509_exact_range_intersects_next_batch_gate.json`
- `Paper-reproduction-apps/librts-paper/data/manifest.json`
- `tests/goal5512_librts_range_intersects_capacity_resolution_test.py`

## Review questions

1. Does the parks record correctly classify the author `cudaErrorMemoryAllocation`
   as an author capacity failure, not an author/RTDL semantic mismatch?
2. Does the lakes retry demonstrate an author/RTDL same-input count match after
   moving serialization away from the workspace quota path?
3. Does the gate distinguish one count match from one author capacity failure
   and avoid an unresolved or silently missing state?
4. Are the parks and lakes geometry/query SHA-256 identities tied to the
   verified archive extraction?
5. Does the gate preserve count-level scope and avoid any pair-row claim?
6. Are complete matrix, Figure 6, full paper, performance ratio, zero-copy,
   author parity, and Embree claims all explicitly closed?
7. Does the result avoid treating the author capacity failure as permission to
   add an app-specific RTDL workaround?
8. Is future parks capacity work correctly separated as a new scope?

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

- Do not call parks.bz2 a semantic mismatch.
- Do not call the lakes count match pairwise relation equality.
- Do not call this a complete 42-pair matrix or Figure 6 reproduction.
- Do not report a performance ratio.
- Do not claim full-paper reproduction, zero-copy, author parity, or Embree
  evidence.
