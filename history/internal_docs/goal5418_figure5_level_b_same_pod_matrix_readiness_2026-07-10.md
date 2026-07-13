# Goal5418 - Figure 5 Level-B Same-POD Matrix Readiness

## Verdict

```text
completed_figure5_level_b_same_pod_execution_packet_ready__dry_run_only
```

Goal5418 builds the executable command packet for the Goal5417 Figure-5-like
Level-B same-POD matrix. It does **not** execute the matrix and does **not**
claim Figure 5 reproduction, exact paper input status, or any author-vs-RTDL
performance ratio.

## Result Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json
```

Key fields:

```text
schema = rtdl.paper_reproduction.xhd.goal5418.figure5_level_b_same_pod_matrix_readiness.v1
status = figure5_level_b_same_pod_matrix_execution_packet_ready__dry_run_only
matched = true
dry_run_only = true
same_pod_execution_claimed = false
matrix_rows_executed = 0
```

## What Was Implemented

Added the app-owned packet builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.py
```

The builder reads:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json
```

and emits a dry-run command/readiness packet. It intentionally does not invoke
POD, SSH, the author binary, or RTDL route runners.

## Primary Graphics Rows

The execution packet includes three primary Level-B public graphics cases:

| Case | Prior status | Commands generated |
|---|---|---:|
| `dragon_happy` | author rerun and RTDL scalar value match paper-branch author-log line within tolerance | 1 author + 2 RTDL |
| `thai_happy_scaled` | author rerun and RTDL scalar value match paper-branch author-log line within tolerance | 1 author + 2 RTDL |
| `thai_asian_scaled` | author rerun and RTDL scalar value match paper-branch author-log line within tolerance | 1 author + 2 RTDL |

Total command count:

```text
graphics_case_count = 3
graphics_command_count = 9
```

The packet includes author `hd_exec` commands and RTDL `run_xhd_rtdl_hd_exec.py`
commands. It preserves the planned denominator columns from Goal5417:

```text
author_running_avg_time_ms
author_reported_time_ms
author_process_wall_sec
rtdl_route_wall_sec
rtdl_process_wall_sec
rtdl_input_load_sec
per_source_witness_exact
cold_or_warm_process
same_pod_gpu
ratio_authorized
```

The RTDL graphics commands also carry the required public-graphics preprocessing
contract:

```text
--translate-each-input-to-min-bound
```

This is not optional for the current Level-B graphics rows.  Earlier
Dragon/HappyBuddha and ThaiStatuette gates established that the author-compatible
public-graphics comparison uses per-input min-bound translation.  Omitting this
flag changes the scalar HDResult and invalidates the matrix row.

## Deferred Secondary Geo Rows

The two bounded geo rows remain present but explicitly deferred:

```text
county_zcta_bounded
water_bg_bounded
```

Reason:

```text
Bounded geo rows use partner/Triton gate scripts rather than the current
graphics hd_exec-compatible route packet. They should be executed only after
paths and runner family are restated in a separate geo execution packet.
```

This avoids mixing graphics `hd_exec`-compatible execution with bounded geo
partner/Triton execution in the same unreviewed command packet.

## POD Policy

The readiness packet carries the required POD wrapper policy:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
naked_ssh_allowed = false
```

Goal5418 itself did not need a POD endpoint.

## Claim Boundary

Authorized:

- a Figure-5-like Level-B same-POD execution command packet;
- three graphics command rows ready for a future POD execution goal;
- RTDL graphics commands that explicitly include the min-bound translation
  preprocessing contract;
- two bounded geo rows deferred to a separate geo packet;
- denominator column preservation;
- wrapper-only POD execution policy.

Not authorized:

- same-POD execution result;
- Figure 5 reproduction;
- exact paper dataset reproduction;
- author-vs-RTDL performance ratio;
- full X-HD paper reproduction;
- treating `fast-scalar` as exact per-source witness reproduction when
  `per_source_witness_exact=false`.

## Validation

Commands:

```text
$env:PYTHONPATH='src'; py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.py
$env:PYTHONPATH='src'; py -m py_compile Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.py
$env:PYTHONPATH='src'; py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json > $null
$env:PYTHONPATH='src'; py -m unittest tests.goal5418_figure5_level_b_same_pod_matrix_readiness_test tests.goal5417_figure5_level_b_same_pod_matrix_plan_test tests.goal5416_full_reproduction_priority_refresh_test
```

Result:

```text
Ran 17 tests in 0.005s
OK
```

The local launcher printed the known environment warning:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Recommended Next Goal

```text
Goal5419_run_figure5_level_b_same_pod_graphics_matrix_on_pod
```

Goal5419 should require a current POD endpoint, run wrapper preflight first,
then execute the graphics rows from the Goal5418 packet. It must report all
denominator columns side-by-side and still refuse ratios unless an external
same-denominator review explicitly authorizes one.
