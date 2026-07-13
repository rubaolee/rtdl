# Goal5358 - X-HD Author-Like Radius Queue Reference

## Status

```text
implemented_review_pending
```

Exit label:

```text
author_like_queue_reference_ready__route_implementation_still_required
```

## Purpose

Goal5357 showed that the current cell-MBR route matches the bounded3d HDResult
but does not emit author-like radius queue iterations. Goal5358 builds the
missing semantic target: an app-owned author-like radius queue reference derived
from generic RTDL nearest/witness primitives.

This is not the final route and not author RT-core parity. It is a reference
schema and correctness target for the next route implementation.

## Files

Added:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5358_author_like_radius_queue_reference.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5358_author_like_radius_queue_reference.json
tests/goal5358_author_like_radius_queue_reference_test.py
```

## Artifact

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5358_author_like_radius_queue_reference.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5358.author_like_radius_queue_reference.v1
```

Status:

```text
author_like_radius_queue_reference_matches_bounded3d_author_trace
```

## Method

The reference uses app-neutral RTDL primitives:

```text
generic_pairwise_l2_distance_candidate_rows
-> generic_nearest_witness_columns
-> generic_max_nearest_distance_with_witness
```

Then it simulates author-like queue rows:

```text
Iteration
Radius
NumInputPoints
NumOutputPoints
CMax2
```

For each iteration:

```text
NumInputPoints = current unresolved source count
NumOutputPoints = count of sources whose exact nearest distance remains greater than Radius
CMax2 = max nearest-distance squared over the current input queue
```

When `NumOutputPoints` is nonzero, the next radius is to be computed by the
generic `radius_growth_step` helper. The bounded3d case is terminal at the
first iteration, so no radius update is needed in this artifact.

## Bounded3d Result

Input:

```text
bounded3d_a.wkt -> bounded3d_b.wkt
```

Author row:

```text
Iteration = 1
Radius = 2.0
NumInputPoints = 9
NumOutputPoints = 0
CMax2 = 4.0
```

RTDL author-like reference row:

```text
Iteration = 1
Radius = 2.0
NumInputPoints = 9
NumOutputPoints = 0
CMax2 = 4.0
```

Comparison:

```text
matched = true
mismatch_count = 0
```

Pipeline metadata:

```text
app_semantics = none
candidate_row_count = 72
nearest_source_count = 9
max_contract = generic_max_nearest_distance_with_witness
```

## Claim Boundary

Goal5358 does not claim:

```text
author tune_radius route mapping
author RT-core algorithm equivalence
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
```

It also does not replace the current cell-MBR route:

```text
current_cell_mbr_route_replaced = false
explicit_author_tune_radius_supported = false
```

Allowed claim:

```text
RTDL now has an app-owned author-like radius queue reference that reproduces
the bounded3d author queue fields using generic nearest/witness primitives.
This gives the next route implementation a concrete comparable trace target.
```

Forbidden summaries:

```text
RTDL supports author -tune_radius.
The cell-MBR route now matches author queue semantics.
Goal5358 proves author RT-core parity.
Goal5358 improves performance.
Goal5358 reproduces Figure 8.
Goal5358 completes full X-HD paper reproduction.
```

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5358_author_like_radius_queue_reference.py --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5358_author_like_radius_queue_reference.json

py -m unittest tests.goal5358_author_like_radius_queue_reference_test tests.goal5357_author_rtdl_radius_trace_comparison_test tests.goal5356_route_radius_trace_metadata_test tests.goal5355_radius_trace_mapping_test tests.goal5354_radius_growth_schedule_test tests.goal5353_xhd_author_rt_option_surface_gate_test
```

Result:

```text
Ran 27 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

The next goal should implement a route variant, not another reference:

```text
implement_cell_mbr_author_like_queue_route_using_this_iteration_schema
```

That route must emit comparable rows:

```text
Iteration
Radius
NumInputPoints
NumOutputPoints
```

and then pass a trace comparison against author `hd_exec` before explicit
author `-tune_radius` can be accepted.

POD expectation:

```text
Goal5358 itself does not need POD. A future route implementation gate may need
POD if it runs the OptiX backend or regenerates author traces.
```
