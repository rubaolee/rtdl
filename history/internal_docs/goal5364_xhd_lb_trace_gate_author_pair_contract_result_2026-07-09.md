# Goal5364 - X-HD lb Trace Gate Author-Pair Contract

Status: `implemented_review_pending`

Date: 2026-07-09

## Purpose

Goal5364 converts the existing Goal5296 author-only `lb=0` / `lb=256`
Level-B diagnostic into an explicit contract for the next RTDL counterpart run.

This goal does not run RTDL and does not authorize explicit `-lb` support.  It
defines the exact fields and pass/fail conditions that the next RTDL gate must
meet.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5364_lb_trace_gate_author_pair_contract.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5364_lb_trace_gate_author_pair_contract.json
tests/goal5364_lb_trace_gate_author_pair_contract_test.py
```

## Input Evidence

Goal5364 consumes:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5296_level_b_dragon_asian_lb_diagnostic_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5363_lb_heavy_offload_semantics_audit.json
```

Goal5296 provides the author-only Level-B pair:

```text
input1 = /tmp/xhd_goal5234/data/dragon.ply
input2 = /tmp/xhd_goal5234/data/asian_dragon.ply
level  = level_b_temporary_input_author_only_diagnostic
```

This is not an exact paper dataset and not Figure 7.

## Author Pair

### `lb=0`

```text
HDResult = 52.453487396240234
Running.AvgTime = 107.254 ms
process wall = 16.25388788431883 s
LargeCells = 0
WL = 3,501,160
WL Heavy Peak = 0
iteration 3 OffloadingSize = 0
iteration 3 RTTime = 96.854 ms
iteration 3 CUDATime = 0.054 ms
```

### `lb=256`

```text
HDResult = 52.453487396240234
Running.AvgTime = 131.841 ms
process wall = 17.09253077954054 s
LargeCells = 5060
WL = 3,501,160
WL Heavy Peak = 217,071,920
iteration 3 OffloadingSize = 27,133,990
iteration 3 RTTime = 45.519 ms
iteration 3 CUDATime = 75.923 ms
```

Author pair validity:

```text
HDResult equal = true
lb0 offload = 0
lb256 offload > 0
```

## RTDL Counterpart Contract

The next gate must run RTDL on the same input pair and produce two counterpart
runs.

### RTDL `lb=0` / disabled-offload counterpart

Required:

```text
HDResult = 52.453487396240234
OffloadingSize = 0
WL Heavy Peak = 0
```

Allowed implementation:

```text
Use a threshold larger than every cell point count or an explicit
disabled-offload mode; record the exact mechanism.
```

### RTDL `lb=256` / heavy-offload counterpart

Required:

```text
HDResult = 52.453487396240234
OffloadingSize > 0
WL Heavy Peak > 0
candidate threshold mapping = max_inline_points=256
```

Comparison rules:

```text
HDResult must match per run.
lb0 offload fields must be zero.
lb256 offload fields must be positive when author fields are positive.
Any byte ratio requires same denominator; otherwise report author-width and
generic RTDL bytes separately.
No performance comparison is authorized by this gate.
```

## Decision

Goal5364 result:

```text
status = bounded_lb_trace_gate_author_pair_ready__rtdl_counterpart_missing
matched = true
author_pair_ready = true
rtdl_counterpart_run_available = false
explicit_lb_support_authorized = false
```

Exit label:

```text
bounded_lb_trace_gate_author_pair_ready__next_run_rtdl_counterpart
```

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5364_lb_trace_gate_author_pair_contract.py
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5364_lb_trace_gate_author_pair_contract.json
py -m unittest tests.goal5364_lb_trace_gate_author_pair_contract_test tests.goal5363_lb_heavy_offload_semantics_audit_test tests.goal5362_tune_radius_option_surface_gate_test tests.goal5353_xhd_author_rt_option_surface_gate_test tests.goal5296_xhd_level_b_lb_diagnostic_test tests.goal5292_xhd_figure7_load_balance_audit_test
```

Result:

```text
Ran 21 tests OK
```

The local Python runtime printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Claim Boundary

Allowed:

```text
The Level-B author lb=0/lb=256 pair is ready as an RTDL counterpart contract.
The next step is to run RTDL lb0/lb256 counterpart runs on the same input.
```

Not authorized:

```text
explicit -lb support
author RT-core algorithm parity
Figure 7 reproduction
Figure 11 reproduction
same-denominator memory claim
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```
