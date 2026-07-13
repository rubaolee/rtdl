# Call For Review: Goal5274 X-HD hd_exec Memory Accounting Integration

Please strictly review Goal5274.

## Files To Review

- Result report:
  `history/internal_docs/goal5274_xhd_hd_exec_memory_accounting_integration_result_2026-07-09.md`
- Updated entrypoint:
  `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py`
- Memory helper from Goal5273:
  `Paper-reproduction-apps/x-hd-paper/scripts/xhd_memory_accounting.py`
- Example artifact:
  `Paper-reproduction-apps/x-hd-paper/results/xhd_goal5274_hd_exec_memory_accounting_attached_example_2026-07-09.json`
- Tests:
  - `tests/goal5274_xhd_hd_exec_memory_accounting_integration_test.py`
  - `tests/goal5274_xhd_hd_exec_memory_accounting_artifact_test.py`
  - `tests/goal5273_xhd_rtdl_memory_accounting_test.py`

## Context

Goal5273 created a separate RTDL memory accounting boundary.  Goal5274 wires
that boundary into the app-owned RTDL `hd_exec`-compatible JSON output through
an opt-in flag:

```text
--include-memory-accounting
```

The integration places status-bearing RTDL accounting under:

```text
Running.Repeats[0].Memory
RTDL.memory_accounting
```

This intentionally does **not** mimic the author's raw numeric Figure 11
`Memory` dict because RTDL still cannot honestly report `BVH` or
`WL Heavy Peak`.

## Review Questions

1. Is `--include-memory-accounting` correctly opt-in, preserving the default
   hd_exec-compatible output?
2. Is `Running.Repeats[0].Memory` clearly status-bearing RTDL accounting rather
   than the author's raw Figure 11 memory schema?
3. Does the integration keep unavailable fields visible with `bytes=null` /
   unavailable status instead of silently zeroing them?
4. Does the example artifact avoid claiming a new route execution?
5. Does the public-columnar route fail closed with
   `memory_accounting_unavailable_for_selected_route` rather than inventing
   grid/frontier values?
6. Are the claim-boundary flags sufficient to prevent Figure 11 reproduction,
   author memory parity, exact allocator telemetry, and performance-ratio
   overclaims?
7. Is it acceptable to expose this memory accounting in the author-shaped JSON
   location while using a different status-bearing schema?
8. Do the tests cover both supported cell-MBR attachment and unsupported
   public-columnar fallback?
9. Does this goal correctly leave native allocator/BVH/heavy-worklist telemetry
   as the next blocker?
10. Should Goal5274 close as
   `completed_hd_exec_status_bearing_memory_accounting_integration__figure11_not_reproduced`?

## Expected Answer Shape

Please respond with:

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to the 10 review questions:
```

Be harsh about any ambiguity that could make users read RTDL's status-bearing
`Memory` object as author Figure 11 parity.
