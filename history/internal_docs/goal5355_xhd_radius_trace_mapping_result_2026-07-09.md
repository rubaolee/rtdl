# Goal5355 - X-HD Radius Trace Mapping

## Status

```text
implemented_review_pending
```

Exit label:

```text
radius_trace_mapping_verified_for_available_author_json__await_route_trace_gate
```

## Purpose

Goal5354 extracted the author RT `tune_radius` update rule into the generic
RTDL `radius_growth_step` / `radius_growth_trace` helper. Goal5355 verifies the
next narrower question: can that generic helper replay the radius transitions
already present in available author `hd_exec` JSON traces?

This goal does **not** execute an RTDL cell-MBR route, does **not** enable
explicit author `-tune_radius`, and does **not** claim author RT-core algorithm
equivalence. It only maps existing author iteration trace fields to the generic
schedule helper.

## Evidence Artifact

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5355_radius_trace_mapping.json
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5355_radius_trace_mapping.py
```

Regression test:

```text
tests/goal5355_radius_trace_mapping_test.py
```

Artifact schema:

```text
rtdl.paper_reproduction.xhd.goal5355.radius_trace_mapping.v1
```

Artifact status:

```text
radius_trace_mapping_matches_available_author_json__route_still_fail_closed
```

## Trace Mapping Method

For each author JSON case, the builder reads:

```text
Running.Repeats[0].GridResolution
Running.Repeats[0].HDUpperBound
Running.Repeats[0].Iterations[*].Radius
Running.Repeats[0].Iterations[*].NumInputPoints
Running.Repeats[0].Iterations[*].NumOutputPoints
Input.Files[1].MBR
```

The target-cell diagonal is derived from the target input metadata:

```text
cell_diagonal = diagonal(Input.Files[1].MBR / Running.Repeats[0].GridResolution)
```

This follows the author directed-Hausdorff input contract already proven in the
X-HD line: input1 is source/query and input2 is target/grid.

Each adjacent author iteration pair is checked by calling:

```text
radius_growth_step(
    radius = current_iteration.Radius,
    hd_upper_bound = Running.Repeats[0].HDUpperBound,
    cell_diagonal = derived_target_cell_diagonal,
    last_input_count = current_iteration.NumInputPoints,
    next_input_count = current_iteration.NumOutputPoints,
    mode = Running.TuneRadius or "adaptive",
)
```

The predicted `next_radius` is compared to the following author iteration's
`Radius` with tolerance `1e-6`.

## Cases

Three available author JSON cases are included:

```text
full_public_dragon_happy_buddha_goal5186
res4full_dragon_happy_buddha_perf
bounded3d_author_gate
```

Summary:

```text
case_count = 3
transition_case_count = 2
total_transition_count = 2
all_transition_cases_matched = true
```

The two transition-bearing cases both match:

```text
full_public_dragon_happy_buddha_goal5186:
  observed next radius  = 0.1377279907464981
  predicted next radius = 0.13772799169519143
  abs diff              = 9.48693318347793e-10

res4full_dragon_happy_buddha_perf:
  observed next radius  = 0.15791678428649902
  predicted next radius = 0.15791678945732696
  abs diff              = 5.1708279324991224e-09
```

The bounded3d case has only one iteration and `NumOutputPoints=0`. The helper
also stops updating when the unresolved output count is zero, so it is retained
as a terminal-stop check rather than a transition case.

## Current X-HD Mapping Status

```text
author_json_trace_mapping_available = true
route_uses_tune_radius_helper = false
run_xhd_rtdl_hd_exec_explicit_tune_radius_still_fail_closed = true
```

Interpretation:

```text
Existing author JSON traces validate the schedule transition math.
They do not prove that the RTDL cell-MBR route follows the same iteration trace.
Explicit author -tune_radius must remain fail-closed until a route trace gate passes.
```

## Claim Boundary

Goal5355 does not claim:

```text
author RT-core algorithm equivalence
author tune_radius route mapping
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
```

Allowed claim:

```text
The generic RTDL radius_growth_step helper can replay the available author
hd_exec radius transition traces when supplied with target MBR, grid resolution,
HD upper bound, previous radius, and in/out queue counts.
```

Forbidden summaries:

```text
RTDL now supports author -tune_radius.
RTDL reproduces the author RT radius loop.
RTDL reproduces Figure 8.
Goal5355 improves performance.
Goal5355 closes author RT-core parity.
```

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5355_radius_trace_mapping.py --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5355_radius_trace_mapping.json

py -m unittest tests.goal5355_radius_trace_mapping_test tests.goal5354_radius_growth_schedule_test tests.goal5353_xhd_author_rt_option_surface_gate_test
```

Observed result:

```text
Ran 17 tests OK
```

The local Python launcher may print the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

Recommended next target:

```text
add_app_owned_radius_trace_metadata_to_cell_mbr_route_under_internal_flag
```

That goal should:

```text
1. keep explicit author -tune_radius fail-closed by default;
2. add app-owned internal trace metadata to the RTDL X-HD route;
3. compare author and RTDL radius/input/output iteration traces on a bounded or Level-B input;
4. only then decide whether explicit author -tune_radius can become supported.
```

POD expectation:

```text
No POD is needed for Goal5355 review.
POD becomes useful for the next route-trace gate only if author hd_exec and
RTDL route traces must be collected on a bounded or Level-B input.
```
