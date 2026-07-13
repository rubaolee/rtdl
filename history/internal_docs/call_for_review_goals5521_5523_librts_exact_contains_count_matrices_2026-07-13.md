# Call For Review: Goals5521-5523 LibRTS Exact Contains Count Matrices

Please jointly review the completion of the exact archive range-contains and
point-contains count matrices.

## Results

- Goal5521: parks.bz2 range-contains five cardinalities match; overall
  range-contains coverage becomes 14/14.
- Goal5522: parks.bz2 point-contains five cardinalities match; unique coverage
  becomes 10/14.
- Goal5523: parks_Europe point-contains five cardinalities match; overall
  point-contains coverage becomes 14/14.

## Primary files

- `history/internal_docs/goal5521_librts_parks_bz2_range_contains_cardinality_result_2026-07-13.md`
- `history/internal_docs/goal5522_librts_parks_bz2_point_contains_cardinality_result_2026-07-13.md`
- `history/internal_docs/goal5523_librts_point_contains_count_matrix_closeout_2026-07-13.md`
- `Paper-reproduction-apps/librts-paper/results/goal5521_parks_bz2_range_contains_cardinality_gate.json`
- `Paper-reproduction-apps/librts-paper/results/goal5522_parks_bz2_point_contains_cardinality_gate.json`
- `Paper-reproduction-apps/librts-paper/results/goal5523_parks_europe_point_contains_cardinality_gate.json`
- `Paper-reproduction-apps/librts-paper/extend_verified_operation_batch.py`
- `Paper-reproduction-apps/librts-paper/run_goal5522_parks_bz2_point_contains_cardinality_gate.py`
- `tests/goal5521_librts_parks_bz2_range_contains_cardinality_test.py`
- `tests/goal5522_librts_verified_batch_extension_test.py`
- `tests/goal5522_librts_parks_bz2_point_contains_cardinality_test.py`
- `tests/goal5523_librts_parks_europe_point_contains_cardinality_test.py`

## Review questions

1. Are all inputs tied to the MD5-verified official archive and per-file hashes?
2. Are the query batches distinct rather than replay?
3. Are the 14/14 coverage calculations correct for both operations?
4. Do all author/RTDL counts match exactly?
5. Are prior 100K checkpoints separated from newly added inventory pairs?
6. Is WKT/cache/extraction work correctly app-owned?
7. Does RTDL remain a generic AABB column/prepared-count system?
8. Is count equality clearly separated from pointwise relation equality?
9. Are performance, Figure 6, full-paper, author-parity, zero-copy, and Embree
   claims correctly closed?

## Requested answer shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-9:
```
