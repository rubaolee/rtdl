# Call For Review: Goal5515 LibRTS Range-Intersects Mismatch Resolution

Please review Goal5515 as a bounded evidence-resolution goal.

## Files

- `history/internal_docs/goal5515_librts_range_intersects_select001_correction_result_2026-07-12.md`
- `Paper-reproduction-apps/librts-paper/results/goal5515_range_intersects_select001_correction_gate.json`
- `Paper-reproduction-apps/librts-paper/build_goal5515_librts_range_intersects_select001_correction_gate.py`
- `tests/goal5515_librts_range_intersects_select001_correction_test.py`
- prior baseline: `history/internal_docs/goal5500_librts_exact_range_intersects_six_geometry_batch_result_2026-07-12.md`

## Review questions

1. Does the current evidence use the same official archive query family and
   preserve the distinction between historical mismatch and current recheck?
2. Are the historical deltas (+3,791 and +54,695) faithfully compared with
   current zero deltas, without claiming an unproven universal root cause?
3. Is the five-match plus one author-capacity-failure state represented
   correctly, with the capacity failure kept separate from semantic evidence?
4. Does the result preserve count-level-only semantics because the author
   binary emits no pair rows?
5. Does the generic float32 indexed-AABB correction remain app-neutral and
   avoid LibRTS-specific behavior in RTDL core?
6. Are the full 42-pair matrix, Figure 6, performance ratio, zero-copy,
   author-parity, full-paper, and Embree claims correctly left closed?
7. Is the result suitable to mark `implemented` but not self-upgrade to
   externally reviewed or complete paper reproduction?

## Requested answer shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-7:
```
