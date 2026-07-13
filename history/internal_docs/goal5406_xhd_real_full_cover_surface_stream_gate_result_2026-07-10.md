# Goal5406 - X-HD Real Full-Cover Surface Stream Gate Result

Date: 2026-07-10

## Goal

Goal5406 advances beyond Goal5405's bounded 56+6 rows/active bridge by
generating the **real full-public RTDL full-cover surface** and computing a
deterministic row summary.

The goal is not to prove explicit `-lb` support. The goal is to determine
whether the closest known generic RTDL surface from Goals5392-5394 can be
generated on the real Dragon -> AsianDragon workload, and then compare that
surface against the Goal5387 author trace v2 oracle.

## Result

POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5406_real_full_cover_surface_stream_gate_pod.json
```

Status:

```text
status  = real_full_cover_surface_generated__author_delta_remaining
matched = true
```

Core numbers:

```text
active queries                         = 437,645
RTDL full-cover rows                    = 24,508,120
Goal5365 full-cover rows                = 24,508,120
author Goal5387 raw offload rows        = 27,133,990
delta author - RTDL full-cover          = 2,625,870
RTDL / author row ratio                 = 0.9032258064516129
```

Hash / sample evidence:

```text
RTDL full-cover row hash                = 9732286907904247845
author raw offload row hash             = 4333109858711462591
hash parity                             = false

RTDL sample source ids                  = [0, 218822, 437644]
RTDL sample cell ids                    = [785, 1554, 2307]
```

Timing from the POD run:

```text
total_sec                               ~= 30.6506
frontier_rows_sec                       ~= 7.4860
trace_summary_sec                       ~= 21.9410
```

The high trace-summary time is expected: the current generic summary hashes
24.5M rows in Python/NumPy-visible memory. This timing is diagnostic only and
is not an X-HD performance claim.

## What Changed

New files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5406_real_full_cover_surface_stream_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5406_real_full_cover_surface_stream_gate_pod.json
tests/goal5406_real_full_cover_surface_stream_gate_test.py
```

No RTDL core/native code was changed for Goal5406.

The new runner:

```text
1. loads the full public Dragon -> AsianDragon inputs;
2. builds the generic grid-cell MBR structure;
3. invokes the existing generic native OptiX cell-MBR frontier producer;
4. filters real offload frontier rows;
5. computes the generic active-query status summary hash/sample;
6. compares count/hash/sample/status evidence against the Goal5387 author trace.
```

## Validation

Local structural tests before POD artifact:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5406_real_full_cover_surface_stream_gate_test

Ran 4 tests
OK (skipped=1)
```

POD preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight

POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

POD focused test before real run:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
python3 -m unittest tests.goal5406_real_full_cover_surface_stream_gate_test

Ran 4 tests
OK (skipped=1)
```

POD real full-cover run:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
export RTDL_OPTIX_LIB=/root/rtdl_goal5093/build/librtdl_optix.so
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5406_real_full_cover_surface_stream_gate.py \
  --input1 /tmp/xhd_goal5234/data/dragon.ply \
  --input2 /tmp/xhd_goal5234/data/asian_dragon.ply \
  --collect-frontier-native-phase-timings

status  = real_full_cover_surface_generated__author_delta_remaining
matched = true
```

Local artifact regression after download:

```text
$env:PYTHONPATH='src'; py -m unittest \
  tests.goal5406_real_full_cover_surface_stream_gate_test \
  tests.goal5405_full_cover_delta_status_bridge_test \
  tests.goal5394_full_cover_delta_status_probe_test \
  tests.goal5392_lb_denominator_surface_reconciliation_test

Ran 17 tests
OK
```

## What This Proves

Goal5406 proves:

```text
the real full-public RTDL full-cover surface can be generated;
the real surface row count is 24,508,120;
the real surface matches the Goal5365 full-cover row-count evidence;
the real surface has a deterministic generic row hash and sample;
the real surface remains short of the author Goal5387 stream by 2,625,870 rows;
the real surface hash does not match the author raw offload row hash.
```

This is stronger than Goal5405 because Goal5405 used a bounded 2-active-query
fixture, while Goal5406 generates the real full-public surface.

## What This Does Not Prove

Goal5406 does not prove:

```text
explicit X-HD -lb support;
Goal5387 row-count parity;
Goal5387 row hash/sample parity;
Goal5387 feedback parity;
Figure 7 reproduction;
Figure 11 reproduction;
author performance parity;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

The reason is concrete:

```text
RTDL full-cover rows = 24,508,120
author raw rows      = 27,133,990
delta                = 2,625,870 = 6 * 437,645
```

## Interpretation

Goal5406 narrows the explicit `-lb` problem.

Before Goal5406, the project had:

```text
bounded 56+6 bridge evidence;
older full-cover count evidence;
no current full-cover row hash/sample gate.
```

After Goal5406, the project has:

```text
real full-cover row-count evidence;
real full-cover hash/sample evidence;
confirmed author delta of exactly 6 rows/active;
confirmed hash mismatch against the author trace.
```

Therefore the next problem is no longer whether RTDL can produce the
full-cover 56x surface. It can. The next problem is the missing 6 rows/active
and the feedback/status semantics that create the author's 62x stream.

## Recommended Next Goal

Recommended Goal5407:

```text
isolate_real_full_cover_to_author_delta_or_fail_close_explicit_lb
```

Goal5407 should compare the real full-cover samples/hash shape against author
trace v2 and decide whether the missing 6 rows/active can be explained by
generic status transitions / feedback, or whether it requires X-HD-specific
author semantics.

Goal5407 must not:

```text
hard-code 6 rows per active;
hard-code 62 rows per active;
claim explicit -lb support before row/hash/status/feedback parity;
claim Figure 7 or Figure 11 reproduction;
add X-HD option names or author-only constants to RTDL core/native.
```

## Claim Boundary

Allowed summary:

```text
Goal5406 generated the real full-public RTDL full-cover surface and showed it
matches the known 24,508,120-row full-cover count. It still differs from the
author Goal5387 stream by 2,625,870 rows and by row hash, so explicit -lb
remains unsupported.
```

Forbidden summaries:

```text
Goal5406 proves explicit -lb support;
Goal5406 reproduces Figure 7;
Goal5406 matches author row hash;
Goal5406 closes the 6 rows/active delta;
Goal5406 completes full X-HD paper reproduction.
```
