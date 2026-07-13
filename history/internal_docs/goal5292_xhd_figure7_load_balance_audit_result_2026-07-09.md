# Goal5292 - X-HD Figure 7 Load-Balance Source / Log Audit

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5292 audits the author-side evidence for X-HD Figure 7 before any RTDL
execution work.

Figure 7 is the load-balance / heavy-cell offload effectiveness figure.  It
needs a same-author denominator with load balancing disabled and enabled, plus
phase fields for RT shader time, CUDA offload kernel time, and total timing.

This goal does not run RTDL and does not compute any RTDL/author performance
ratio.  It asks a narrower question:

```text
Do the pinned author source and checked-in logs contain enough evidence to
reproduce Figure 7, or is the author-side lb=0/lb=256 matrix missing?
```

## Implementation

New app-owned audit builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure7_load_balance_audit.py
```

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5292_figure7_load_balance_audit_2026-07-09.json
```

Focused regression:

```text
tests/goal5292_xhd_figure7_load_balance_audit_test.py
```

No RTDL core or native files were changed.

## Inputs

The builder reads:

```text
.codex_tmp/xhd_author_repo
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_matrix_2026-07-08.json
```

Pinned author commit:

```text
7bf41c8442d059c94f4178355c6d5a10571d9658
```

Audited author files:

```text
expr/run_lb.sh
expr/draw_lb.py
expr/logs/lb_comparison/...
expr/logs/end2end/rt_gpu/...
```

## Author Script Evidence

`expr/run_lb.sh` is present and lists four graphics pairs:

```text
dragon.ply -> asian_dragon.ply
thai_statuette.ply -> happy_buddha.ply
dragon.ply -> happy_buddha.ply
thai_statuette.ply -> asian_dragon.ply
```

It runs:

```text
variant = rt
execution = gpu
lb values = [0, 256]
profiling flag present = true
check flag present = true
```

But at the pinned main commit, `run_lb.sh` lists graphics pairs only:

```text
script_lists_geo_pairs = false
script_lists_graphics_pairs = true
```

`expr/draw_lb.py` is also present.  It expects both geo and graphics
`lb_comparison` directories:

```text
logs/lb_comparison/lb_0/geo
logs/lb_comparison/lb_256/geo
logs/lb_comparison/lb_0/graphics
logs/lb_comparison/lb_256/graphics
```

It derives stacked components:

```text
BVHBuildup
LBKernel
RTShader
```

and uses iteration fields:

```text
AdjustBVHTime
CUDATime
RTTime
Hits
ComparedPoints
```

The artifact records:

```text
script_draw_contract_mismatch = true
```

Reason:

```text
draw_lb.py expects both geo and graphics lb_comparison logs, but run_lb.sh at
the pinned main commit lists only graphics pairs.
```

## Checked-In Log Evidence

The checked-in `expr/logs/lb_comparison` matrix is absent:

```text
lb_comparison total_json_count = 0
complete_lb0_lb256_matrix_present = false
```

All expected Figure-7-style directories have zero JSON files:

```text
expr/logs/lb_comparison/lb_0/geo      = 0
expr/logs/lb_comparison/lb_256/geo    = 0
expr/logs/lb_comparison/lb_0/graphics = 0
expr/logs/lb_comparison/lb_256/graphics = 0
```

The checked-in `expr/logs/end2end/rt_gpu` records do contain useful profiling
fields, but only for `LB=256` records:

```text
record_count = 7
has_lb0_records = false
has_lb256_records = true
has_iteration_metrics = true
```

Category coverage:

```text
geo:
  record_count = 3
  lb_values = [256]
  records_with_iteration_profiling = 3

graphics:
  record_count = 4
  lb_values = [256]
  records_with_iteration_profiling = 4
```

Interpretation:

```text
run_all rt_gpu logs contain per-iteration RTTime/CUDATime/OffloadingSize fields
for geo and graphics, but they are LB=256 records only and do not provide the
lb=0 vs lb=256 matrix that draw_lb.py requires for Figure 7.
```

## Decision

Goal5292 reports:

```text
status = figure7_load_balance_source_audit_ready__figure7_not_reproduced__lb_comparison_logs_missing
figure7_reproduced = false
lb_comparison_numeric_matrix_available = false
run_all_iteration_metrics_available = true
run_all_lb0_counterpart_available = false
author_script_available = true
```

Current blocker:

```text
Author source contains Figure 7 scripts, and run_all contains profiling-style
iteration fields for LB=256 records, but checked-in lb_comparison lb=0/lb=256
logs are absent. Figure 7 reproduction requires rerunning or reconstructing the
author lb_comparison matrix with exact or explicitly Level-B inputs.
```

## Claim Boundary

Allowed:

```text
Figure 7 author-side source/log audit is ready.
Author run_lb.sh and draw_lb.py are present at the pinned main commit.
Checked-in lb_comparison logs are missing.
run_all rt_gpu logs contain LB=256 profiling-style iteration fields only.
Figure 7 remains not reproduced.
```

Not authorized:

```text
Figure 7 reproduced
exact paper dataset reproduction
RTDL/author load-balance parity
author-vs-RTDL performance ratio
lb2048 or any other substitute treated as Figure 7
full X-HD paper reproduction
```

## Validation

Commands run:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure7_load_balance_audit.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure7_load_balance_audit.py
py -m unittest tests.goal5292_xhd_figure7_load_balance_audit_test
```

Local Python printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

All commands exited successfully.

Focused test result:

```text
Ran 3 tests in 0.096s
OK
```

## POD Usage

No POD was required for Goal5292.  This is an author source/log audit over
checked-in files.

A POD becomes relevant only if the next approved step is to regenerate the
author `lb_comparison` matrix by running `run_lb.sh` or equivalent author
commands.

## Next Recommended Step

Do not start RTDL Figure 7 comparison work yet.  Choose one:

```text
1. If exact HDDatasets inputs are available on a POD, run author run_lb.sh or
   equivalent commands to regenerate lb_comparison logs.
2. If exact inputs are unavailable, define a separately named Level-B
   load-balance diagnostic and do not call it Figure 7 reproduction.
3. Move to another paper blocker whose author-side denominator is stronger.
```

Any future Figure 7 execution goal should first produce an author-side
`lb=0`/`lb=256` numeric matrix with clear input provenance.  Only then should
RTDL comparison or performance work begin.
