# Call For Review - Goal5170 Parallel Grouped Frontier Nearest Continuation

Date: 2026-07-08

Please strictly review Goal5170:

```text
history/internal_docs/goal5170_parallel_grouped_frontier_nearest_continuation_result_2026-07-08.md
```

Relevant implementation and tests:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
tests/goal5170_parallel_grouped_frontier_nearest_continuation_test.py
tests/goal5163_numba_frontier_nearest_continuation_test.py
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_serial_frontier_continuation_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5170_parallel_frontier_continuation_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
```

## Review Questions

1. Is the grouped parallel implementation race-free, i.e. does each parallel
   task own one query row's best witness state?
2. Do the tests cover non-contiguous frontier rows for the same query and a
   pruned row, rather than only an already-contiguous happy path?
3. Does `numba_parallel` preserve seeded current-best semantics and the
   lower-item-id tie-break compared with NumPy and serial Numba?
4. Does `auto` choose the new parallel executor only when Numba is available,
   with `numpy` and explicit serial `numba` still available?
5. Do the route/matrix scripts expose and record
   `frontier_nearest_executor`, `nearest_executor`, and
   `nearest_reduction_strategy` so POD artifacts self-identify the executed
   path?
6. Does the POD evidence show the full public res4 route still matches author
   HDResult under `validation_mode=author-only`?
7. Is the reported performance delta supported by the same-POD serial-vs-parallel
   control matrices, and is it framed as a modest route improvement rather than
   a paper-performance or parity claim?
8. Does the implementation remain app-neutral, with no X-HD or paper-app
   identity in RTDL core?
9. Does the report avoid claiming full paper reproduction, exact paper dataset
   reproduction, author algorithm equivalence, or denominator-aligned
   author-performance parity?
10. Should Goal5170 be added as a review-pending addendum to the existing
    Goals5130-5164 packet and the Goal5165-5169 addenda?

## Requested Verdict Label

```text
approve_goal5170_parallel_grouped_frontier_nearest_continuation
```
