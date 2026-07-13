# Goal5367 - X-HD lb Author-Radius Probe

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5366 showed that author `OffloadingSize` and RTDL
`heavy_offload_peak_rows` use compatible byte formulas, but row-count parity is
not established.  One possible explanation was that the Goal5365 RTDL route used
the single-pass full-cover radius:

```text
RTDL full-cover radius = 266.9466183641096
author iteration_3 radius = 79.2156982421875
```

Goal5367 tests that explanation by running RTDL lb256 again on the same
Dragon -> AsianDragon Level-B input with explicit radius equal to the author
iteration radius.

## Files

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5367_rtdl_lb256_author_radius_probe_pod.json
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5367_lb_author_radius_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5367_lb_author_radius_probe.json
tests/goal5367_lb_author_radius_probe_test.py
```

## POD

POD:

```text
213.173.108.24:13502
```

Access method:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 exec "<cmd>"
```

Remote workspace:

```text
/tmp/rtdl_goal5364
```

The remote workspace already had the current RTDL minimal package and OptiX
native build from Goal5365.

## Probe Command

The probe is the Goal5365 lb256 route with one change:

```text
--radius 79.2156982421875
```

The route still uses:

```text
--input1 /tmp/xhd_goal5234/data/dragon.ply
--input2 /tmp/xhd_goal5234/data/asian_dragon.ply
--translate-each-input-to-min-bound
--grid-shape 96,60,72
--max-inline-points 256
--initial-state none
--grid-cell-builder native_cuda
--frontier-inline-nearest
```

## Result

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5367_lb_author_radius_probe.json
```

Status:

```text
author_radius_lb_probe_ready__radius_alignment_not_sufficient_for_row_parity
```

Exit label:

```text
author_radius_alignment_preserves_value_but_not_lb_denominator_parity
```

## Comparison

Author lb256:

```text
HDResult = 52.453487396240234
OffloadingSize = 27,133,990
WL Heavy Peak = 217,071,920 bytes
iteration_3 radius = 79.2156982421875
```

RTDL full-cover lb256 from Goal5365:

```text
radius = 266.9466183641096
HDResult = 52.453491321261296
heavy_offload_peak_rows = 24,508,120
rtdl_route_sec = 38.40844701975584
```

RTDL author-radius lb256 probe:

```text
radius = 79.2156982421875
HDResult = 52.453491321261296
heavy_offload_peak_rows = 21,006,960
rtdl_route_sec = 28.31456644833088
```

## Interpretation

The explicit author-radius run:

```text
preserves HD value: true
aligns radius: true
closes row-count denominator gap: false
```

In fact, it reduces RTDL heavy rows relative to the full-cover route:

```text
24,508,120 - 21,006,960 = 3,501,160 fewer rows
```

and moves farther away from author `OffloadingSize`:

```text
27,133,990 - 21,006,960 = 6,127,030 rows
RTDL author-radius / author ratio = 0.7741935483870968
```

Therefore the denominator gap is not solved by radius alignment alone.  The
next parity target must align author queue / `in_queue` / `cmin2` / offload
iteration semantics.

## Validation

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5367_lb_author_radius_probe.py
py -m unittest tests.goal5367_lb_author_radius_probe_test tests.goal5366_lb_denominator_reconciliation_test tests.goal5365_rtdl_lb_counterpart_gate_test tests.goal5364_lb_trace_gate_author_pair_contract_test tests.goal5363_lb_heavy_offload_semantics_audit_test
Ran 16 tests OK
```

Known local Python launcher noise:

```text
Could not find platform independent libraries <prefix>
```

Tests passed.

## Decision

```text
explicit_lb_support_authorized_now = false
row_count_parity_authorized_now = false
```

## Claim Boundary

Not authorized:

```text
explicit -lb support
row-count parity
same-denominator memory parity
Figure 7 reproduction
Figure 11 reproduction
author RT-core algorithm parity
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Next Gate

```text
author_queue_aligned_lb_trace_with_in_queue_cmin2_and_raw_offload_denominator
```

The next gate cannot only set the scalar radius. It must match the author
iteration model more deeply:

```text
same active in_queue;
same cmin2/current-best state model;
same offload append denominator;
same threshold;
same preprocessing;
same author-width byte view.
```
