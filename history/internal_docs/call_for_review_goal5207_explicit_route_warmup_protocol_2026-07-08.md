# Call For Review: Goal5207 Explicit Route Warmup Protocol

Date: 2026-07-08

Please strictly review Goal5207.

Files under review:

```text
history/internal_docs/goal5207_explicit_route_warmup_protocol_result_2026-07-08.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5207_explicit_route_warmup_protocol_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5207_explicit_warmup_all_then_measured_all_graphics_dragon_happy_buddha_2026-07-08.json
```

## Reviewer Questions

1. Does `--route-warmup-source-limit` accept a positive integer or `all`, reject
   out-of-range values, and preserve existing measured `--source-limits`
   behavior?
2. Is the warmup case recorded separately under top-level `route_warmup` rather
   than mixed into `cases`?
3. Is the warmup case marked with:

```text
case_role = warmup
excluded_from_summary_statistics = true
```

4. Do summary statistics (`median_route_wall_sec`, `max_route_wall_sec`,
   `all_matched`, row counts) use only measured cases?
5. Does the POD artifact still match the Goal5186 author HDResult for both
   warmup and measured all-source cases?
6. Does the artifact support the reported numbers:

```text
warmup route ~= 1.176s
measured warm route ~= 0.626s
load_full_inputs ~= 0.685s
total including load + warmup + measured ~= 2.893s
```

7. Does the result correctly state that the warm measured route is a
   same-process / prepared-regime metric and must not replace the fresh
   one-shot headline?
8. Does this goal avoid claiming a new RTDL route optimization, exact paper
   dataset reproduction, full paper reproduction, author parity, or an
   author-vs-RTDL ratio?
9. Is it acceptable that this is an app-owned performance protocol rather than
   an RTDL core API?
10. Should Goal5207 close as:

```text
completed_explicit_route_warmup_protocol__warm_metric_separated_from_fresh
```

Expected answer shape:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 10 questions:
```
