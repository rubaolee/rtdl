# Call For Review - Goal5361 X-HD Res4Full Nonterminal Author Queue Gate

Please strictly review Goal5361.

## Files To Review

Implementation:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5358_author_like_radius_queue_reference.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5359_cell_mbr_author_like_queue_route.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5361_res4full_nonterminal_author_queue_gate.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5361_res4full_nonterminal_author_queue_wrapper_output.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5361_res4full_nonterminal_author_queue_gate.json
```

Tests:

```text
tests/goal5361_res4full_nonterminal_author_queue_gate_test.py
tests/goal5360_hd_exec_author_queue_wrapper_gate_test.py
tests/goal5359_cell_mbr_author_like_queue_route_test.py
tests/goal5358_author_like_radius_queue_reference_test.py
tests/goal5149_cell_mbr_frontier_nearest_continuation_test.py
```

Report:

```text
history/internal_docs/goal5361_xhd_res4full_nonterminal_author_queue_gate_result_2026-07-09.md
```

## Context

Goal5360 integrated a terminal bounded3d author-like queue route into the
`hd_exec`-compatible RTDL wrapper. Goal5361 tests a nonterminal res4full
Dragon -> HappyBuddha case where author JSON has:

```text
Iteration 1: NumInputPoints=5205, NumOutputPoints=4
Iteration 2: NumInputPoints=4,    NumOutputPoints=0
```

This goal should prove a bounded internal diagnostic route can match the
available nonterminal author radius queue trace. It should not claim explicit
author `-tune_radius` support, Figure 8 reproduction, author RT-core parity,
performance, or full X-HD paper reproduction.

## Review Questions

1. Does `nearest_witness_from_cell_mbr_frontier_numpy_columns(..., allow_missing=True)` keep the default public behavior fail-closed while enabling an explicit app-neutral partial-nearest route for orchestration?
2. Is the missing-nearest fallback still generic (`pairwise_l2_distance_candidate_rows -> nearest_witness`) and not X-HD-specific?
3. Does the res4full wrapper evidence correctly identify `translate_each_input_to_min_bound` as required by the author JSON MBR?
4. Does the Goal5361 artifact truly match author and RTDL rows for both iterations within tolerance, including `Radius`, `NumInputPoints`, `NumOutputPoints`, and `CMax2`?
5. Is the revised `CMax2` model (`author_like_global_cmax2_state_confirmed_points_only`) a reasonable bounded diagnostic match for this no-offload res4full trace?
6. Does the route actually exercise `radius_growth_step` on a nonterminal iteration (`NumOutputPoints > 0`)?
7. Does the wrapper still keep explicit author `-tune_radius` unsupported / unmapped rather than quietly accepting the author option?
8. Do the tests cover both the high-level nonterminal author queue match and the lower-level default-fail-closed / explicit-allow-missing behavior?
9. Are the claim boundaries correct: no author RT-core parity, no Figure 8 reproduction, no performance claim, no full paper reproduction?
10. Should Goal5361 close the immediate "find nonterminal trace case and run wrapper route" item from Goal5360?

## Expected Answer Shape

Please answer with:

```text
Verdict: approve / approve_with_required_amendments / block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
10. ...
```

Suggested approve label if accepted:

```text
approve_goal5361_res4full_nonterminal_author_queue_gate
```
