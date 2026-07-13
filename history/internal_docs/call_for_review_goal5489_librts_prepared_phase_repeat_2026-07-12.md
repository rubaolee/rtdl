# Call For Review: Goal5489 LibRTS Same-Process Prepared Phase Repeat

Please review the implementation and POD evidence for Goal5489. This is an
app-owned measurement goal following the generic `Aabb2DColumns` front door;
it does not change RTDL core and does not authorize a performance ratio.

## Files

- implementation:
  `Paper-reproduction-apps/librts-paper/run_exact_point_contains_prepared_phase_columns_repeat.py`
- test: `tests/goal5489_librts_prepared_phase_repeat_test.py`
- result:
  `Paper-reproduction-apps/librts-paper/results/librts_goal5489_dtl_cnty_repeat.json`
- report:
  `history/internal_docs/goal5489_librts_prepared_phase_repeat_result_2026-07-12.md`

## Review questions

1. Does the runner prepare one generic columnar AABB index and execute the same
   query batch repeatedly in one process, rather than rebuilding per iteration?
2. Are all repeated result counts checked against the same-input author count?
3. Are first-use and subsequent-query phases reported separately without
   calling the difference a speedup?
4. Does the evidence preserve exact archive/member SHA-256 identity and prove
   the author and RTDL saw the same files?
5. Does the implementation remain app-owned, with no LibRTS/X-HD or paper
   identity added to RTDL core?
6. Is the author internal query time kept separate from RTDL route wall and
   primitive time, with `performance_ratio_authorized=false`?
7. Does the claim boundary correctly exclude pointwise relation equivalence,
   Figure 6 reproduction, full paper reproduction, device zero-copy, and
   Embree?
8. Are the local test, manifest, and machine-readable POD result sufficient
   to close this diagnostic goal, subject to external review?

## Expected answer shape

```text
Verdict: approve | revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
```
