# Call For Review: Goal5514 LibRTS Exact `select_0.01` Six-Geometry Resolution

Please strictly review Goal5514 as a bounded exact-input count/capacity
resolution goal, not as a complete paper-reproduction or performance result.

## Files to review

- `history/internal_docs/goal5514_librts_exact_range_intersects_select001_resolution_result_2026-07-12.md`
- `Paper-reproduction-apps/librts-paper/results/goal5514_exact_range_intersects_select001_resolution_gate.json`
- `Paper-reproduction-apps/librts-paper/results/goal5514_lakes_bz2_select_0.01_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5514_parks_bz2_select001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5513_exact_range_intersects_select001_gate.json`
- `Paper-reproduction-apps/librts-paper/data/manifest.json`
- `tests/goal5514_librts_range_intersects_select001_resolution_test.py`

## Review questions

1. Does the six-case gate correctly report five same-input count matches and
   one author CUDA capacity failure?
2. Is parks.bz2 explicitly prevented from becoming a semantic mismatch or an
   RTDL failure when the author failed before comparison?
3. Does the lakes.bz2 checkpoint preserve exact input identity and count
   equality after the temporary serialize-path workaround?
4. Are the five matches count-level only because the author binary exposes no
   pair rows for this operation?
5. Does the gate avoid complete 42-pair, Figure 6, full-paper, performance,
   zero-copy, author-parity, and Embree claims?
6. Is the six-geometry `.01` family clearly separated from the remaining
   archive pairs and from other query families?
7. Does the package preserve generic RTDL core ownership and avoid adding an
   app-specific workaround for parks capacity?
8. Are all six states checkpointed or explicitly classified, with no hidden
   unresolved case?

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

- Do not call this the complete 42-pair range-intersects matrix.
- Do not infer pairwise relation equality from count equality.
- Do not call the parks author capacity failure a semantic mismatch.
- Do not report a performance ratio.
- Do not claim Figure 6, full-paper reproduction, zero-copy, author parity,
  native algorithm equivalence, or Embree evidence.
