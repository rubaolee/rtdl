# Call For Review: Goal5273 X-HD RTDL Memory Accounting Boundary

Please strictly review Goal5273.

## Files To Review

- Result report:
  `history/internal_docs/goal5273_xhd_rtdl_memory_accounting_boundary_result_2026-07-09.md`
- RTDL memory accounting artifact:
  `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5273_rtdl_memory_accounting_boundary_2026-07-09.json`
- Memory accounting helper:
  `Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py`
- Tests:
  - `tests/goal5273_xhd_rtdl_memory_accounting_test.py`
  - `tests/goal5273_xhd_rtdl_memory_accounting_boundary_artifact_test.py`
- Prior author memory matrix:
  `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5272_figure11_author_memory_log_matrix_2026-07-09.json`

## Context

Goal5272 extracted the author's Figure 11 memory matrix from the author
`draw_mem.py` and `logs/mem` artifacts.  Goal5273 does not reproduce Figure 11.
It defines the RTDL-side accounting boundary so later work cannot mix estimated
route memory, unavailable native allocator fields, and author memory logs into a
single misleading total.

## Review Questions

1. Does the Goal5273 artifact correctly keep `figure11_reproduced=false` and
   avoid any author-memory-parity or exact-GPU-allocator claim?
2. Is the mapping from author fields (`BVH`, `Grid`, `MBRs B`, `WL`,
   `WL Heavy Peak`) to RTDL statuses honest?
3. Are unavailable fields represented as unavailable with `bytes=null`, rather
   than silently treated as zero?
4. Are `Grid` and `MBRs B` estimates grounded in generic route metadata rather
   than X-HD-specific hard-coded constants?
5. Is the `WL` estimate correctly tied to `frontier_row_capacity`, and is the
   fast-scalar frontier example clearly marked as not a Figure 11 reproduction
   row?
6. Are RTDL-only fields (`input_column_matrices_and_ids`, `nearest_state`)
   separated from author Figure 11 fields?
7. Do the tests adequately prevent future overclaiming of Figure 11
   reproduction or author-memory parity?
8. Does the result report avoid comparing RTDL estimated totals to author X-HD
   totals as if they were same-denominator memory measurements?
9. Is the recommended next work correct: either expose real allocator/BVH/heavy
   worklist telemetry, or integrate explicit status-bearing accounting into the
   hd_exec-compatible output?
10. Should Goal5273 close as
   `completed_rtdl_memory_accounting_boundary__figure11_not_reproduced`?

## Expected Answer Shape

Please respond with:

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to the 10 review questions:
```

The review should be harsh about any wording that turns this accounting boundary
into a Figure 11 reproduction claim.  The acceptable result is a boundary, not a
paper figure.
