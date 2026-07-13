# Goal5362 - X-HD Narrow tune_radius Option-Surface Gate

## Status

```text
implemented_review_pending
```

Exit label:

```text
narrow_internal_adaptive_tune_radius_option_mapping_ready
```

## Purpose

Goal5361 proved that the internal `cell-mbr-author-queue-diagnostic` route can
match an available nonterminal author radius queue trace:

```text
5205 input points -> 4 output points -> 0 output points
```

Goal5362 makes the next option-surface decision. It does **not** make
`-tune_radius` generally supported. It authorizes only this narrow mapping:

```text
-tune_radius adaptive
  allowed only for:
    --rtdl-route cell-mbr-author-queue-diagnostic
    --author-trace-json <nonterminal author trace>
```

All other explicit author RT options remain fail-closed unless a separate
semantic mapping goal proves them.

## Implementation

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

The author RT option surface now distinguishes:

```text
supported_explicit_author_rt_options
unsupported_explicit_author_rt_options
all_explicit_author_rt_options_supported
```

The narrow support predicate is:

```text
route_label == "cell-mbr-author-queue-diagnostic"
and explicit -tune_radius == adaptive
and --author-trace-json contains a nonterminal transition
```

A nonterminal transition means:

```text
Running.Repeats[0].Iterations has at least two rows
and at least one row has NumOutputPoints > 0
```

The route metadata now reports:

```text
RTDL.radius_trace_metadata.author_tune_radius_supported
RTDL.radius_trace_metadata.author_tune_radius_support_scope
```

The CLI help text was also narrowed so users do not read this as full
author RT-core support.

## Evidence Artifact

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5362_tune_radius_option_surface_gate.py
```

Summary artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_option_surface_gate.json
```

Wrapper outputs:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_adaptive_supported_output.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_double_fail_closed.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_tune_radius_terminal_trace_fail_closed.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5362_other_author_rt_option_fail_closed.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5362.tune_radius_option_surface_gate.v1
```

Status:

```text
narrow_internal_adaptive_tune_radius_mapping_passed
```

## Positive Case

Command shape:

```text
cell-mbr-author-queue-diagnostic
+ res4full nonterminal author trace
+ --translate-each-input-to-min-bound
+ -tune_radius adaptive
```

Result:

```text
exit_code = 0
supported_explicit_author_rt_options = ["tune_radius"]
unsupported_explicit_author_rt_options = []
all_explicit_author_rt_options_supported = true
```

Author HDResult:

```text
0.1241602823138237
```

RTDL HDResult:

```text
0.12416027787377293
```

Absolute difference:

```text
4.440050771492565e-09
```

Queue rows still match Goal5361:

```text
Iteration 1:
  Radius          author=0.1218298003077507  rtdl=0.1218298003077507
  NumInputPoints  author=5205                rtdl=5205
  NumOutputPoints author=4                   rtdl=4
  CMax2           author=0.014842499978840351
                  rtdl=0.014842500243026413

Iteration 2:
  Radius          author=0.15791678428649902 rtdl=0.15791678945732696
  NumInputPoints  author=4                   rtdl=4
  NumOutputPoints author=0                   rtdl=0
  CMax2           author=0.015415775589644909
                  rtdl=0.015415774601692507
```

The route metadata reports:

```text
uses_radius_growth_step = true
author_tune_radius_supported = true
```

## Fail-Closed Controls

### 1. Unsupported tune_radius mode

```text
-tune_radius double
exit_code = 2
status = unsupported_author_rt_options_fail_closed
unsupported_explicit_author_rt_options = ["tune_radius"]
route_executed = false
```

### 2. Terminal trace does not qualify

```text
bounded3d author trace
-tune_radius adaptive
exit_code = 2
status = unsupported_author_rt_options_fail_closed
unsupported_explicit_author_rt_options = ["tune_radius"]
route_executed = false
```

This preserves Goal5360's terminal-trace fail-closed boundary.

### 3. Other author RT option still fails

```text
res4full nonterminal author trace
-tune_radius adaptive
-lb 0
exit_code = 2
status = unsupported_author_rt_options_fail_closed
supported_explicit_author_rt_options = ["tune_radius"]
unsupported_explicit_author_rt_options = ["lb"]
route_executed = false
```

This proves the gate is not simply "all explicit author options accepted once
the route label is diagnostic." Only the evidenced adaptive tune-radius mapping
is allowed.

## What This Proves

Goal5362 proves:

1. Explicit `-tune_radius adaptive` can be accepted under the internal
   diagnostic route when a nonterminal author trace is supplied.
2. The accepted case still matches author HDResult and queue rows.
3. Unsupported tune-radius modes, terminal traces, and other author RT options
   still fail closed before route execution.

## What This Does Not Prove

Goal5362 does not claim:

```text
general author tune_radius support
author RT-core algorithm equivalence
Figure 8 reproduction
performance improvement
exact paper dataset reproduction
full X-HD paper reproduction
```

The support scope remains:

```text
Internal diagnostic route only; requires --author-trace-json with a nonterminal
author radius trace. This is not author RT-core algorithm parity, Figure 8
reproduction, or a performance claim.
```

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5362_tune_radius_option_surface_gate.py

py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5362_tune_radius_option_surface_gate.json

py -m unittest tests.goal5362_tune_radius_option_surface_gate_test tests.goal5361_res4full_nonterminal_author_queue_gate_test tests.goal5360_hd_exec_author_queue_wrapper_gate_test tests.goal5359_cell_mbr_author_like_queue_route_test tests.goal5358_author_like_radius_queue_reference_test tests.goal5149_cell_mbr_frontier_nearest_continuation_test
```

Observed test result:

```text
Ran 18 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

Recommended next actions:

1. Send Goals5357-5362 for strict review as the current radius / tune-radius
   semantics packet.
2. If approved, update the review register and decide whether this internal
   diagnostic mapping should remain internal-only or become part of a broader
   app-owned author-option compatibility mode.
3. Do not claim Figure 8, author RT-core parity, or performance until a
   denominator-aligned figure / route goal proves those separately.
