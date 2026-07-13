# Call For Review - Goal5365 X-HD RTDL lb Counterpart Gate

Please strictly review Goal5365.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5365_rtdl_lb_counterpart_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb0_disabled_raw_dragon_asian_translated_initial_none_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb256_raw_dragon_asian_translated_initial_none_pod.json
tests/goal5365_rtdl_lb_counterpart_gate_test.py
history/internal_docs/goal5365_xhd_rtdl_lb_counterpart_gate_result_2026-07-09.md
```

Input evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5364_lb_trace_gate_author_pair_contract.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json
```

## Review Questions

1. Was the POD used through `scripts/current_pod_ssh.py`, and did the preflight
   pass?
2. Is the minimal RTDL source sync / remote native build evidence sufficient
   for this POD run?
3. Do the RTDL `lb0` and `lb256` counterpart runs use the same Level-B input
   as the author Goal5296 pair?
4. Is `--translate-each-input-to-min-bound` correctly recorded as necessary
   preprocessing, given that the no-translate run returned the wrong value?
5. Do both RTDL runs match the author HDResult within the declared `5e-6`
   behavior-gate tolerance?
6. Does RTDL `lb0` produce zero heavy offload rows / bytes?
7. Does RTDL `max_inline_points=256` produce positive heavy offload rows /
   bytes?
8. Does the report correctly refuse row-count parity and same-denominator byte
   parity because author and RTDL offload counts/bytes differ?
9. Does the report correctly refuse Figure 7 / Figure 11 / performance /
   explicit `-lb` support claims?
10. Should the next decision be either:
    - accept a narrow behavior-level `-lb` mapping under this Level-B gate, or
    - tighten to row-count/denominator parity before exposing `-lb`?

## Expected Verdict Labels

Choose one:

```text
approve_goal5365_rtdl_lb_counterpart_behavior_gate
approve_with_required_amendments
revise_goal5365_rtdl_lb_counterpart_behavior_gate
block_goal5365_rtdl_lb_counterpart_behavior_gate
```

## Allowed Summary If Approved

```text
On the Level-B Dragon->Asian diagnostic pair, RTDL matches author HDResult for
disabled-offload and max_inline_points=256 counterparts, and reproduces the
qualitative offload switch.  This is behavior-level evidence only; it is not
row-count parity, Figure 7/11 reproduction, or explicit -lb support.
```

## Forbidden Summaries

```text
explicit -lb support
author RT-core parity
row-count parity
same-denominator memory parity
Figure 7 reproduction
Figure 11 reproduction
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```
