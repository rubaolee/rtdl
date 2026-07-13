# Call For Review: Goal5517 LibRTS Exact Range-Contains Batch

Please review Goal5517 as a bounded exact-input count gate.

## Files

- `history/internal_docs/goal5517_librts_exact_range_contains_batch_result_2026-07-13.md`
- `Paper-reproduction-apps/librts-paper/results/goal5517_exact_range_contains_batch_gate.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5517_range_contains_batch_extraction.json`
- `Paper-reproduction-apps/librts-paper/build_goal5517_librts_range_contains_batch_gate.py`
- `Paper-reproduction-apps/librts-paper/tools/run_goal5517_range_contains_single_case.py`
- `tests/goal5517_librts_exact_range_contains_batch_test.py`

## Review questions

1. Are the four selected geometry/query pairs valid exact archive members?
2. Do per-member SHA-256 values and same-file flags support same-input use?
3. Do all four author and RTDL counts match exactly?
4. Is the `/tmp` extraction fallback correctly treated as an environment-only
   storage workaround rather than an algorithm or performance change?
5. Does RTDL use only the generic AABB columnar prepared route?
6. Are author internal timing and RTDL load/prepare/query phases kept separate?
7. Is count equality correctly distinguished from pointwise relation equality?
8. Are full matrix, Figure 6, performance, full-paper, zero-copy, author-parity,
   and Embree claims correctly left closed?

## Requested answer shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-8:
```
