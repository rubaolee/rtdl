# Call For Review: Goal5496 LibRTS Exact Range-Intersects Count Gate

Please strictly review Goal5496 and its evidence. Verify the implementation,
the exact archive/member provenance, and the claim boundary. Do not infer
relation-level or performance parity from equal counts.

## Files

- `Paper-reproduction-apps/librts-paper/run_exact_range_intersects_count_gate.py`
- `tests/goal5496_librts_exact_range_intersects_count_gate_test.py`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_extraction.json`
- `Paper-reproduction-apps/librts-paper/results/librts_goal5496_range_intersects_dtl_cnty_gate.json`
- `history/internal_docs/goal5496_librts_exact_range_intersects_dtl_result_2026-07-12.md`

## Review questions

1. Does the selected geometry/query pair appear in the verified Goal5492
   `range_intersects` inventory, and do the final files' SHA-256 values match
   the extraction evidence?
2. Does the gate pass the same unchanged files to the pinned author binary and
   RTDL, with geometry/query counts checked before execution?
3. Does the author parser correctly handle both observed output contracts:
   `Loaded boxes / RT, load...` and `Loaded polygons / Loading Time...`?
4. Is the author `load_factor=1` configuration recorded and is the earlier
   `load_factor=0.0001` CUDA failure treated as a configuration/toolchain
   diagnostic rather than hidden or converted into a correctness claim?
5. Does RTDL use the generic `Aabb2DColumns` prepared AABB front door, without
   LibRTS-specific core/native customization?
6. Are author internal query time, RTDL load, prepare, query wall, and
   primitive phases kept separate, with `performance_ratio_authorized=false`?
7. Does the report explicitly limit the result to count agreement and reject
   pointwise relation equality, Figure 6, full-paper, zero-copy, author parity,
   and Embree claims?
8. Are the local focused tests and POD result sufficient to close the goal as
   implemented but review pending, without self-approval?

## Expected answer shape

```text
Verdict: approve / approve_with_required_amendments / revise
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
Answers 1-8: ...
Requested verdict label: ...
```
