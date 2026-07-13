# Call For Review - Goal5154 X-HD Seeded Performance Matrix

Please strictly review Goal5154.

## Files

- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py`
- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_performance_matrix_pod.json`
- `tests/goal5154_xhd_seeded_performance_matrix_test.py`
- `history/internal_docs/goal5154_xhd_seeded_performance_matrix_result_2026-07-08.md`

## Review Questions

1. Does the runner actually rerun author `hd_exec` and RTDL seeded route on the
   same POD for sample256 and sample1024?
2. Are correctness fields still matched against author HDResult and exact
   reference?
3. Are author `Running.AvgTime`, author process wall, RTDL route time, RTDL total
   time, load time, and exact-reference time separated?
4. Is the decision to withhold speedup/parity ratios correct under the current
   phase mismatch?
5. Does the matrix clearly identify the current gap against author timing
   without overstating performance claims?
6. Does the regression test pin the phase-boundary and no-ratio policy?

## Expected Verdict Shape

```text
verdict_label:
blocking_findings:
required_amendments:
non_blocking_notes:
```
