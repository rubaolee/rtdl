# Call For Review - Goal5355 X-HD Radius Trace Mapping

## Scope

Please strictly review Goal5355:

```text
history/internal_docs/goal5355_xhd_radius_trace_mapping_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5355_radius_trace_mapping.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5355_radius_trace_mapping.json
tests/goal5355_radius_trace_mapping_test.py
src/rtdsl/radius_schedule.py
tests/goal5354_radius_growth_schedule_test.py
```

Goal5355 maps existing author `hd_exec` JSON iteration traces to the generic
RTDL `radius_growth_step` helper created in Goal5354. It does not execute an
RTDL route and does not enable explicit author `-tune_radius`.

## Expected Verdict Labels

Use one of:

```text
approve_goal5355_radius_trace_mapping
approve_with_required_amendments
block_goal5355_radius_trace_mapping
```

## Review Questions

1. Does the builder correctly derive target cell diagonal from
   `Input.Files[1].MBR / Running.Repeats[0].GridResolution`, consistent with
   the already-proven directed input1-to-input2 X-HD contract?
2. Does the builder correctly replay each adjacent author iteration transition
   using `Radius`, `HDUpperBound`, `NumInputPoints`, `NumOutputPoints`, and the
   author `TuneRadius` mode?
3. Do the two transition-bearing author cases genuinely match within `1e-6`,
   and are the reported absolute differences small enough to support the
   trace-mapping claim?
4. Is the bounded3d one-iteration case correctly treated as a terminal
   zero-output stop check rather than as transition evidence?
5. Does this goal correctly preserve the boundary that the RTDL route still
   does not use the helper and explicit author `-tune_radius` remains
   fail-closed?
6. Does the report avoid claiming author RT-core algorithm equivalence,
   author tune-radius route mapping, Figure 8 reproduction, performance
   improvement, or full X-HD paper reproduction?
7. Is it correct that no POD evidence is required for Goal5355 because it
   consumes existing author JSON traces and tests local helper math, while the
   next route-trace comparison may require POD?
8. Is the recommended next target correct: add app-owned radius trace metadata
   to the X-HD cell-MBR route under an internal flag, compare author and RTDL
   traces, and only then consider accepting explicit author `-tune_radius`?

## Expected Answer Shape

Please answer in this structure:

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
2. ...
...
8. ...
```

## Claim Boundary To Enforce

Allowed:

```text
The generic RTDL radius_growth_step helper can replay available author hd_exec
radius transition traces.
Existing author JSON traces provide schedule-math evidence for radius-growth.
The next required step is a route trace gate.
```

Not allowed:

```text
RTDL supports explicit author -tune_radius
author tune_radius route mapping is closed
author RT-core algorithm equivalence
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
```
