# Call For Review - Goal5406 X-HD Real Full-Cover Surface Stream Gate

Date: 2026-07-10

## Files Under Review

```text
history/internal_docs/goal5406_xhd_real_full_cover_surface_stream_gate_result_2026-07-10.md
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5406_real_full_cover_surface_stream_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5406_real_full_cover_surface_stream_gate_pod.json
tests/goal5406_real_full_cover_surface_stream_gate_test.py
```

Related prior evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5365_rtdl_lb_counterpart_gate.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5387_author_trace_v2_execution.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5392_lb_denominator_surface_reconciliation.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5393_lb_status_stream_target_design.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5394_full_cover_delta_status_probe.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5405_full_cover_delta_status_bridge_pod.json
```

## Requested Review

Please strictly review whether Goal5406 correctly advances from the bounded
Goal5405 bridge to a real full-public RTDL full-cover row surface, while still
refusing to overclaim explicit X-HD `-lb` support.

## Context

Goals5392-5394 identified the closest known RTDL surface:

```text
author rows per active     = 62
RTDL full-cover rows/active = 56
missing rows per active     = 6
```

Goal5405 proved that shape only on a bounded two-active-query fixture:

```text
active_count = 2
rows = 124 = 2 * 62
matched = true
```

Goal5406 now runs the real full-public Dragon -> AsianDragon full-cover surface
through the native OptiX cell-MBR frontier row producer and computes a generic
active-query row summary.

POD artifact:

```text
status = real_full_cover_surface_generated__author_delta_remaining
matched = true

RTDL full-cover rows             = 24,508,120
Goal5365 full-cover rows         = 24,508,120
author Goal5387 raw rows         = 27,133,990
delta                            = 2,625,870
RTDL / author row ratio          = 0.9032258064516129
RTDL full-cover row hash         = 9732286907904247845
author raw offload row hash      = 4333109858711462591
hash parity                      = false
```

## Review Questions

1. Does Goal5406 materially advance beyond Goal5405 by generating the real
   full-public full-cover row surface rather than only a bounded fixture?
2. Is the row count evidence internally consistent with Goal5365 and the
   Goal5392/5393/5394 denominator analysis?
3. Is it correct that Goal5406 still does **not** prove author Goal5387
   row-count parity?
4. Is it correct that Goal5406 still does **not** prove author row hash/sample
   parity?
5. Does the new runner use generic RTDL row-table and status-summary APIs
   without adding X-HD-specific semantics to RTDL core/native?
6. Is the POD validation sufficient for this gate?
7. Does the result correctly keep explicit `-lb`, Figure 7, Figure 11,
   performance ratio, exact dataset reproduction, and full paper reproduction
   claims unauthorized?
8. Is the recommended next goal, isolating the real 6 rows/active delta or
   fail-closing explicit `-lb`, the right next step?
9. Are there any concerns with the current hash/sample summary contract for a
   24.5M-row surface?
10. Should Goal5406 close with:

```text
real_full_cover_surface_generated__author_delta_remaining
```

## Expected Answer Shape

Please answer with:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 10 review questions:
```

## Requested Verdict Label

If approved:

```text
approve_goal5406_real_full_cover_surface_generated__author_delta_remaining
```
