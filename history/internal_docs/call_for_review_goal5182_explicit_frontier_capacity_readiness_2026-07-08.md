# Call For Review - Goal5182 X-HD Explicit Frontier Capacity Readiness

Please strictly review Goal5182.

## Files Under Review

Implementation:

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_feasibility_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5182_xhd_explicit_frontier_capacity_test.py
```

Evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_explicit_capacity_readiness_goal5182_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/goal5182_explicit_frontier_capacity_readiness_result_2026-07-08.md
```

## Context

Goal5179 showed the full public Stanford Dragon/HappyBuddha Level B candidate
has:

```text
437645 * 543652 = 237926579540 point pairs
```

so naive pairwise materialization is impossible.

Goal5180 ran a bounded 16-source subset against the full target and matched an
exact subset oracle.

Goal5181 extended that to source limits 16/64/128 and observed:

```text
max_frontier_row_count = 526006
suggested_next_explicit_row_capacity = 789009
```

Goal5182 is the local readiness step before a POD/OptiX capacity gate. It
threads explicit capacity through the route runners and verifies fail-closed
behavior locally.

## Requested Checks

1. Does Goal5182 correctly pass `frontier_row_capacity` through the X-HD route
   runner into generic RTDL frontier helpers, rather than implementing an
   X-HD-specific capacity shortcut?
2. Does the direct route test prove explicit too-small capacity fails closed
   with an overflow error rather than silently truncating frontier rows?
3. Does the local readiness artifact show source limits 16/64/128 all matched
   exact subset oracles with `route_abs_diff=0.0` and explicit capacity
   metadata?
4. Is the capacity value `789009` correctly derived from Goal5181's observed
   `526006` max frontier rows by a 1.5x planning factor?
5. Does the Goal5182 result avoid claiming POD/OptiX native capacity validation,
   all-source route completion, exact paper dataset reproduction, figure
   reproduction, full paper reproduction, or performance ratio?
6. Is it acceptable that Goal5182 is local NumPy readiness only, with the
   actual POD/OptiX capacity gate deferred to the next goal?
7. Did the change preserve prior Goal5180/5181 behavior and nearby native
   frontier tests?
8. Should the next goal be the POD/OptiX bounded gate using
   `--frontier-row-capacity 789009`?

## Expected Answer Shape

Please answer with:

```text
Verdict: <approve / approve_with_required_amendments / block>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to requested checks:
1. ...
2. ...
...
8. ...
```

Requested verdict label if approved:

```text
approve_goal5182_explicit_frontier_capacity_readiness__pod_optix_gate_next
```
