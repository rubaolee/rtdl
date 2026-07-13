# Call For Review - Goal5371 X-HD Inline / Global-Bound lb Probe

Please strictly review Goal5371.

## Files To Review

```text
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_kind_count_probe.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5371_inline_global_bound_lb_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_dragon_asian_lb256_author_radius_inline_kind_count_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_dragon_asian_lb256_author_radius_inline_global_bound_kind_count_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5371_inline_global_bound_lb_probe.json
tests/goal5371_inline_global_bound_lb_probe_test.py
history/internal_docs/goal5371_xhd_inline_global_bound_lb_probe_result_2026-07-09.md
```

## What Goal5371 Claims

Goal5371 tests two denominator hypotheses:

```text
1. The 21,006,960 RTDL author-radius count was caused by host materialization /
   sort rather than native raw counting.

2. Existing RTDL generic global-bound early break approximates author cmax2
   abort semantics and closes the lb denominator gap.
```

Both are rejected by POD evidence:

```text
author OffloadingSize                       = 27,133,990
author-radius materialized rows             = 21,006,960
author-radius inline count-only kind2       = 21,006,960
inline + global-bound count-only kind2      = 21,006,960
global_bound_early_break_count              = 0
no-inline raw kind2 from Goal5368           = 304,981,889
```

## Review Questions

1. Does the generic probe extension correctly expose `--inline-nearest` and
   `--global-bound-early-break` without adding X-HD-specific core behavior?
2. Is the `overflow_telemetry_only` nearest-column tolerance in
   `partner_continuations.py` narrowly scoped and still fail-closed for normal
   inline-nearest routes?
3. Do the two POD artifacts prove that inline count-only kind2 rows equal the
   prior materialized author-radius count?
4. Do the two POD artifacts prove that existing generic global-bound
   early-break did not change this denominator?
5. Are the numeric comparisons correct?
6. Is it correct to reject materialization/sort and existing global-bound as
   explanations for author `OffloadingSize`?
7. Does the report avoid claiming explicit `-lb` support, row parity,
   Figure 7/11 reproduction, author RT-core parity, or performance ratios?
8. Are the tests sufficient for this probe stage?
9. Is the recommended next target correct: author shader status-machine
   semantics (`cmin2`, `cmax2` abort, offload/miss queues, load-balance
   post-processing), or author instrumentation?
10. Can Goal5371 be closed with:

```text
inline_and_global_bound_lb_probes_ready__author_denominator_still_unmatched
```

## Expected Answer Shape

```text
Verdict:
  approve / approve_with_required_amendments / block

Blocking findings:
  ...

Required amendments:
  ...

Non-blocking notes:
  ...

Review question answers:
  1. ...
  ...
  10. ...

Recommended next step:
  ...
```
