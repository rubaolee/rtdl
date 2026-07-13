# Call For Review - Goal5367 X-HD lb Author-Radius Probe

Please strictly review Goal5367.

## Files To Review

```text
history/internal_docs/goal5367_xhd_lb_author_radius_probe_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5367_lb_author_radius_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5367_rtdl_lb256_author_radius_probe_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5367_lb_author_radius_probe.py
tests/goal5367_lb_author_radius_probe_test.py
```

Useful context:

```text
history/internal_docs/goal5366_xhd_lb_denominator_reconciliation_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5366_lb_denominator_reconciliation.json
history/internal_docs/goal5365_xhd_rtdl_lb_counterpart_gate_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
```

## Review Questions

1. Does Goal5367 correctly test the hypothesis that the row-count denominator
   gap was caused by RTDL using the full-cover radius instead of the author
   iteration radius?

2. Does the POD result show that explicit author-radius RTDL preserves the HD
   value but still does not match author `OffloadingSize`?

3. Is the conclusion correct that radius alignment alone is insufficient for
   `-lb` row-count parity?

4. Does the report correctly refuse to authorize explicit `-lb` support,
   Figure 7, Figure 11, same-denominator memory parity, or performance ratios?

5. Is the next gate correctly identified as author-queue-aligned lb trace,
   including `in_queue`, `cmin2`, and raw offload denominator?

6. Are there any hidden X-HD-specific RTDL core changes or overclaims?

## Expected Answer Shape

```text
Verdict: approve_goal5367_author_radius_probe
or
Verdict: approve_with_required_amendments
or
Verdict: block

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to the 6 review questions:
1. ...
```
