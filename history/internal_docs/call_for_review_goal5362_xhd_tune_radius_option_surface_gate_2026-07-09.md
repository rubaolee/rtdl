# Call For Review - Goal5362 X-HD Narrow tune_radius Option-Surface Gate

Please strictly review Goal5362.

## Files To Review

Implementation:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5362_tune_radius_option_surface_gate.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/perf_res4full_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_hd_exec_output_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_option_surface_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_adaptive_supported_output.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_double_fail_closed.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_terminal_trace_fail_closed.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_other_author_rt_option_fail_closed.json
```

Tests:

```text
tests/goal5362_tune_radius_option_surface_gate_test.py
tests/goal5361_res4full_nonterminal_author_queue_gate_test.py
tests/goal5360_hd_exec_author_queue_wrapper_gate_test.py
tests/goal5359_cell_mbr_author_like_queue_route_test.py
tests/goal5358_author_like_radius_queue_reference_test.py
tests/goal5149_cell_mbr_frontier_nearest_continuation_test.py
```

Report:

```text
history/internal_docs/goal5362_xhd_tune_radius_option_surface_gate_result_2026-07-09.md
```

## Context

Goal5353 made explicit author RT options fail closed. Goal5354 extracted a
generic `radius_growth_step` helper. Goal5355 verified that available author
radius traces can be replayed by that helper. Goal5356/5357 showed that the
old single-pass route was not author queue aligned. Goal5358/5359 built an
author-like queue reference and route. Goal5360 exposed the bounded terminal
queue route through the `hd_exec`-compatible wrapper while keeping explicit
`-tune_radius` fail-closed. Goal5361 then matched a nonterminal res4full
author queue trace with `NumOutputPoints > 0` and `uses_radius_growth_step=true`.

Goal5362 decides the next narrow option-surface step:

```text
-tune_radius adaptive
```

is accepted only for:

```text
--rtdl-route cell-mbr-author-queue-diagnostic
--author-trace-json <nonterminal author trace>
```

All other explicit author RT options must remain fail-closed.

## Review Questions

1. Does the implementation keep `-tune_radius` support narrow to `adaptive` plus `cell-mbr-author-queue-diagnostic` plus a nonterminal author trace?
2. Does the positive res4full case still match author HDResult and queue rows within tolerance?
3. Does the positive case correctly record `supported_explicit_author_rt_options=["tune_radius"]`, no unsupported options, and `author_tune_radius_supported=true`?
4. Does `-tune_radius double` still fail closed before route execution?
5. Does `-tune_radius adaptive` still fail closed for the terminal bounded3d trace?
6. Does adding another explicit author RT option such as `-lb 0` still fail closed, while preserving that `tune_radius` itself is the supported option in that mixed case?
7. Does the CLI/help/metadata avoid implying general author tune-radius support?
8. Are the claim boundaries correct: no author RT-core parity, no Figure 8 reproduction, no performance claim, no exact dataset claim, no full paper reproduction?
9. Do the tests cover the positive case and the fail-closed controls well enough?
10. Should Goal5362 close the immediate "decide whether explicit author `-tune_radius` can be accepted under the bounded internal route label" item from Goal5361?

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
approve_goal5362_narrow_internal_adaptive_tune_radius_option_surface_gate
```
