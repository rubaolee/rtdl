# Call For Review: Goal5509 LibRTS Exact Range-Intersects Next Batch

Please strictly review Goal5509 as a bounded evidence goal, not as a full
paper-reproduction or performance goal.

## Files to review

- `history/internal_docs/goal5509_librts_exact_range_intersects_next_batch_result_2026-07-12.md`
- `Paper-reproduction-apps/librts-paper/data/goal5509_range_intersects_next_exact_batch.json`
- `Paper-reproduction-apps/librts-paper/results/goal5509_exact_range_intersects_next_batch_gate.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5509_range_intersects_batch_extraction.json`
- `Paper-reproduction-apps/librts-paper/results/goal5509_parks_Europe_select0001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5509_dtl_cnty_select0001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5509_USACensusBlockGroupBoundaries_select0001_10000.json`
- `Paper-reproduction-apps/librts-paper/results/goal5509_USADetailedWaterBodies_select0001_10000.json`
- `tests/goal5509_librts_range_intersects_next_batch_test.py`

## Review questions

1. Does the input manifest select six verified archive pairs from the exact
   `range-intersects_select_0.0001_queries_10000` family, with the reused
   geometry files and new query members covered by extraction evidence and
   SHA-256 records?
2. Do the four checkpointed cases show same-input author/RTDL count equality?
3. Is the `parks.bz2`/`lakes.bz2` state correctly recorded as unresolved after
   batch resource/process termination, rather than silently treated as a
   mismatch or match?
4. Does the result correctly remain count-level, given that the standard
   author binary does not expose pair rows?
5. Are the Goal5508 native library and generic RTDL columnar front door used,
   with no LibRTS-specific behavior added to RTDL core?
6. Are author internal query time, RTDL load/prepare/query phases, and process
   lifetime kept separate, with no performance ratio claim?
7. Does the package avoid claiming a complete 42-pair matrix, Figure 6,
   full-paper reproduction, relation parity, zero-copy, author parity, or
   Embree evidence?
8. Is the next scope correctly limited to independent checkpointing of the
   two large cases and the remaining exact archive pairs?

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
- Do not turn unresolved large cases into semantic mismatches or matches.
- Do not report a performance ratio from the separated phase fields.
- Do not claim Figure 6, full-paper reproduction, zero-copy, author parity, or
  Embree evidence.
