# Goal5357 - X-HD Author vs RTDL Radius Trace Comparison

## Status

```text
implemented_review_pending
```

Exit label:

```text
current_single_pass_route_not_author_tune_radius_compatible__keep_explicit_tune_radius_fail_closed
```

## Purpose

Goal5355 proved that available author `hd_exec` radius transitions can be
replayed by the generic RTDL `radius_growth_step` helper. Goal5356 added
app-owned RTDL route radius trace metadata and explicitly labeled the current
route as single-pass / not author queue aligned.

Goal5357 performs the next gate: compare existing author radius trace evidence
against the current RTDL route trace metadata and decide whether explicit author
`-tune_radius` can be accepted.

The result is a deliberate negative/control result:

```text
HDResult matches, but radius trace semantics do not match.
```

## Files

Added:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5357_author_rtdl_radius_trace_comparison.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5357_author_rtdl_radius_trace_comparison.json
tests/goal5357_author_rtdl_radius_trace_comparison_test.py
```

## Artifact

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5357_author_rtdl_radius_trace_comparison.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5357.author_rtdl_radius_trace_comparison.v1
```

Status:

```text
trace_comparison_complete__rtdl_value_matches_but_radius_trace_not_author_queue_aligned
```

## Comparison Case

Input:

```text
bounded3d_a.wkt -> bounded3d_b.wkt
```

Author source artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/bounded3d_author_hd_exec_output_pod.json
```

RTDL source artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5356_route_radius_trace_metadata.json
```

## Result

Value result:

```text
author HDResult = 2.0
RTDL HDResult   = 2.0
abs_diff        = 0.0
hd_result_matched = true
```

Trace result:

```text
trace_comparable_as_author_radius_queue = false
trace_matched = false
semantic_mismatch_count = 4
```

Semantic mismatches:

```text
iteration_model:
  author = author_adaptive_radius_queue_loop
  RTDL   = single_pass_cell_mbr_route_not_author_radius_loop

radius:
  author = 2.0
  RTDL   = 3.3166247913554

num_output_points:
  author = 0
  RTDL   = 9

route_uses_radius_growth_helper:
  author = true
  RTDL   = false
```

Interpretation:

```text
The current RTDL route matches bounded3d HDResult but does not emit author-like
radius/input/output queue iterations.
```

## Decision

Explicit author `-tune_radius` must remain fail-closed:

```text
explicit_author_tune_radius_must_remain_fail_closed = true
```

Goal5357 does not authorize silently accepting, ignoring, or partially mapping
the author's `-tune_radius` option.

## Claim Boundary

Goal5357 does not claim:

```text
author tune_radius route mapping
author RT-core algorithm equivalence
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
```

Allowed claim:

```text
On the bounded3d case, current RTDL matches the author HDResult but fails the
author radius-queue trace comparison. Therefore explicit author -tune_radius
must remain fail-closed until a route emits comparable author-like iterations.
```

Forbidden summaries:

```text
RTDL supports author -tune_radius.
RTDL route radius trace matches author radius trace.
RTDL reproduces Figure 8.
Goal5357 proves author RT-core parity.
Goal5357 improves performance.
Goal5357 advances full paper reproduction beyond bounded trace semantics.
```

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5357_author_rtdl_radius_trace_comparison.py --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5357_author_rtdl_radius_trace_comparison.json

py -m unittest tests.goal5357_author_rtdl_radius_trace_comparison_test tests.goal5356_route_radius_trace_metadata_test tests.goal5355_radius_trace_mapping_test tests.goal5354_radius_growth_schedule_test tests.goal5353_xhd_author_rt_option_surface_gate_test
```

Result:

```text
Ran 24 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

The next decision is architectural:

```text
decide_whether_to_build_author_like_radius_queue_route_or_stop_tune_radius_line
```

If we choose to pursue author RT-core trace parity, the next implementation must
build a route variant that emits author-like radius/input/output iterations,
driven by the generic `radius_growth_step` helper. Only after that route passes
an author-vs-RTDL trace comparison should explicit author `-tune_radius` be
considered for support.

POD expectation:

```text
Goal5357 itself uses existing artifacts and does not need POD.
A future author-like queue-route gate may need POD if it regenerates author
hd_exec traces or runs a Level-B route comparison on GPU.
```
