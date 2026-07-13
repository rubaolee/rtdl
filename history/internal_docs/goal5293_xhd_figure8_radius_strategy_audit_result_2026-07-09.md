# Goal5293 - X-HD Figure 8 Radius-Strategy Source / Log Audit

Date: 2026-07-09

## Verdict

```text
implemented_review_pending
```

## Purpose

Goal5293 audits the author-side evidence for X-HD Figure 8 before any RTDL
route or performance work.

Figure 8 is the radius-growing strategy figure.  It compares:

```text
Add by Diagonal
Double Radius
Our Method / adaptive
```

This goal asks whether the pinned author source and checked-in logs already
contain the numeric matrix needed to reproduce that figure.

This goal does not run RTDL and does not compute any RTDL/author performance
ratio.

## Implementation

New app-owned audit builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure8_radius_strategy_audit.py
```

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json
```

Focused regression:

```text
tests/goal5293_xhd_figure8_radius_strategy_audit_test.py
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
expr/run_radius_tuning.sh
expr/draw_tune_radius.py
expr/logs/tune_radius/...
```

## Author Script Evidence

`expr/run_radius_tuning.sh` is present and defines geo and graphics workloads.

Geo pairs:

```text
dtl_cnty.wkt -> uszipcode.wkt
USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt
lakes.bz2.wkt -> parks.bz2.wkt
```

Graphics pairs:

```text
dragon.ply -> asian_dragon.ply
thai_statuette.ply -> happy_buddha.ply
dragon.ply -> happy_buddha.ply
thai_statuette.ply -> asian_dragon.ply
```

The script runs:

```text
variant = rt
execution = gpu
normalize = false
repeat = 1
check = false
tune_radius values = [add, double, adaptive]
```

`expr/draw_tune_radius.py` is present and expects:

```text
logs/tune_radius/rt_gpu_radius_add/geo
logs/tune_radius/rt_gpu_radius_add/graphics
logs/tune_radius/rt_gpu_radius_double/geo
logs/tune_radius/rt_gpu_radius_double/graphics
logs/tune_radius/rt_gpu_radius_adaptive/geo
logs/tune_radius/rt_gpu_radius_adaptive/graphics
```

It plots:

```text
Running.AvgTime
```

and labels:

```text
Add by Diagonal
Double Radius
Our Method
```

The artifact records:

```text
script_draw_contract_aligned = true
```

Meaning:

```text
The author script and plotting file agree on add/double/adaptive radius
strategy labels and geo/graphics categories.
```

## Checked-In Log Evidence

The checked-in `expr/logs/tune_radius` matrix is absent:

```text
root_exists = false
total_json_count = 0
complete_variant_category_matrix_present = false
```

Every expected directory has zero JSON files:

```text
expr/logs/tune_radius/rt_gpu_radius_add/geo = 0
expr/logs/tune_radius/rt_gpu_radius_add/graphics = 0
expr/logs/tune_radius/rt_gpu_radius_double/geo = 0
expr/logs/tune_radius/rt_gpu_radius_double/graphics = 0
expr/logs/tune_radius/rt_gpu_radius_adaptive/geo = 0
expr/logs/tune_radius/rt_gpu_radius_adaptive/graphics = 0
```

The existing paper-branch `run_all` mapping also says:

```text
coverage_status = not_covered_by_run_all_timing_logs
record_count = 0
```

Interpretation:

```text
run_all does not provide Figure 8 radius-strategy evidence. The only obvious
author-side Figure 8 denominator is the tune_radius script/log family, and its
checked-in numeric logs are absent.
```

## Decision

Goal5293 reports:

```text
status = figure8_radius_strategy_audit_ready__figure8_not_reproduced__tune_radius_logs_missing
figure8_reproduced = false
tune_radius_numeric_matrix_available = false
run_all_radius_strategy_evidence_available = false
author_script_available = true
```

Current blocker:

```text
Author source contains run_radius_tuning.sh and draw_tune_radius.py for
add/double/adaptive radius strategies, but checked-in logs/tune_radius has no
JSON records. The paper-branch run_all log mapping also identifies no explicit
radius-growing strategy records. Figure 8 reproduction requires regenerating or
recovering the tune_radius numeric matrix with exact or explicitly Level-B
inputs.
```

## Claim Boundary

Allowed:

```text
Figure 8 author-side source/log audit is ready.
Author radius-tuning scripts are present and internally aligned.
Checked-in tune_radius logs are missing.
Figure 8 remains not reproduced.
```

Not authorized:

```text
Figure 8 reproduced
exact paper dataset reproduction
RTDL/author radius-strategy parity
author-vs-RTDL performance ratio
run_all logs treated as Figure 8
full X-HD paper reproduction
```

## Validation

Commands run:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure8_radius_strategy_audit.py
py -m py_compile Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure8_radius_strategy_audit.py
py -m unittest tests.goal5293_xhd_figure8_radius_strategy_audit_test
```

Local Python printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

All commands exited successfully.

Focused test result:

```text
Ran 3 tests in 0.060s
OK
```

## POD Usage

No POD was required for Goal5293.  This is an author source/log audit over
checked-in files.

A POD becomes relevant only if the next approved step is to run
`run_radius_tuning.sh` or equivalent author commands to regenerate the
`tune_radius` matrix.

## Next Recommended Step

Do not start RTDL Figure 8 comparison work yet.  Choose one:

```text
1. If exact HDDatasets inputs are available on a POD, run author
   run_radius_tuning.sh or equivalent commands to regenerate tune_radius logs.
2. If exact inputs are unavailable, define a separately named Level-B
   radius-strategy diagnostic and do not call it Figure 8 reproduction.
3. Move to another paper blocker whose author-side denominator is stronger.
```

Any future Figure 8 execution goal should first produce an author-side
add/double/adaptive numeric matrix with clear input provenance.  Only then
should RTDL comparison or performance work begin.
