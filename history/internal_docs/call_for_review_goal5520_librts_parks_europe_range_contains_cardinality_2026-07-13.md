# Call For Review: Goal5520 Parks-Europe Range-Contains Cardinalities

Please review Goal5520 as an exact-input count-level cardinality matrix.

## Files

- `history/internal_docs/goal5520_librts_parks_europe_range_contains_cardinality_result_2026-07-13.md`
- `Paper-reproduction-apps/librts-paper/results/goal5520_parks_europe_range_contains_cardinality_gate.json`
- `Paper-reproduction-apps/librts-paper/results/goal5520_parks_europe_cardinality_pod_raw.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5520_parks_europe_cardinality_extraction.json`
- `Paper-reproduction-apps/librts-paper/build_goal5520_parks_europe_range_contains_cardinality_gate.py`
- `Paper-reproduction-apps/librts-paper/run_goal5520_parks_europe_range_contains_cardinality_gate.py`
- `tests/goal5520_librts_parks_europe_range_contains_cardinality_test.py`

## Review questions

1. Are all five geometry/query identities exact official archive members?
2. Do all five author and RTDL counts match exactly?
3. Are the four runtime query batches correctly separated from the Goal5517
   100K prior checkpoint?
4. Are all five query hashes distinct, excluding same-input replay?
5. Is the AABB cache correctly kept app-owned?
6. Does RTDL use only the generic prepared AABB column route?
7. Does coverage honestly remain 9/14 rather than complete?
8. Are relation, performance, figure, full-paper, zero-copy, author-parity,
   and Embree claims correctly left closed?

## Requested answer shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-8:
```
