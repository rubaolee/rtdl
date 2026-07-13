# Goal5359 - X-HD Cell-MBR Author-Like Queue Route

## Status

```text
implemented_review_pending
```

Exit label:

```text
bounded_cell_mbr_queue_route_trace_matches__wrapper_integration_still_required
```

## Purpose

Goal5358 built an author-like queue reference from generic exact nearest
primitives. Goal5359 moves that queue schema onto the existing app-owned
cell-MBR route internals.

The route variant:

1. runs the directed cell-MBR route at the current radius;
2. consumes emitted per-source nearest columns;
3. derives `NumOutputPoints` from sources whose nearest distance remains greater
   than the current radius;
4. emits author-like queue rows;
5. uses `radius_growth_step` for future nonterminal iterations.

The bounded3d case is terminal in one iteration, so no radius update is needed
in this artifact.

## Files

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
```

The update adds a default-off internal hook:

```text
emit_nearest_columns = False
```

When enabled by the Goal5359 route builder, `_directed_cell_mbr_route` returns
per-source nearest columns. Existing route summaries are unchanged by default.

Added:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5359_cell_mbr_author_like_queue_route.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5359_cell_mbr_author_like_queue_route.json
tests/goal5359_cell_mbr_author_like_queue_route_test.py
```

## Artifact

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5359_cell_mbr_author_like_queue_route.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5359.cell_mbr_author_like_queue_route.v1
```

Status:

```text
cell_mbr_author_like_queue_route_matches_bounded3d_author_trace
```

## Bounded3d Result

Input:

```text
bounded3d_a.wkt -> bounded3d_b.wkt
```

Author queue row:

```text
Iteration = 1
Radius = 2.0
NumInputPoints = 9
NumOutputPoints = 0
CMax2 = 4.0
```

RTDL cell-MBR queue route row:

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

## Route Evidence

The route evidence shows this is not only the Goal5358 reference:

```text
uses_cell_mbr_route = true
uses_emitted_nearest_columns = true
backend = numpy
route_iteration_model = cell_mbr_author_like_radius_queue_route
```

Per-iteration route internals:

```text
frontier_row_count = 9
candidate_distance_evaluations = 72
route_distance = 2.0
route_contract = generic_cell_mbr_nearest_frontier_reference
nearest_columns_contract = generic_nearest_witness_from_cell_mbr_frontier
nearest_columns_app_semantics = none
```

Because the bounded3d author case has `NumOutputPoints=0` in the first
iteration, this artifact does not exercise a nonterminal radius update:

```text
uses_radius_growth_step = false
```

That is an honest property of this bounded case, not a route parity claim for
nonterminal `tune_radius` behavior.

## Claim Boundary

Goal5359 does not claim:

```text
author tune_radius route mapping
author RT-core algorithm equivalence
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
```

It also does not yet expose the route through the hd_exec-compatible wrapper:

```text
explicit_author_tune_radius_supported_by_hd_exec = false
```

Allowed claim:

```text
The app-owned cell-MBR route can now emit bounded3d author-like queue fields
that match the author trace, using emitted per-source nearest columns.
Wrapper integration and nonterminal radius-update validation remain open.
```

Forbidden summaries:

```text
RTDL supports author -tune_radius.
The hd_exec-compatible wrapper now accepts -tune_radius.
Goal5359 proves author RT-core parity.
Goal5359 reproduces Figure 8.
Goal5359 improves performance.
Goal5359 completes full X-HD paper reproduction.
Goal5359 proves nonterminal radius-growth behavior.
```

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5359_cell_mbr_author_like_queue_route.py --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5359_cell_mbr_author_like_queue_route.json

py -m unittest tests.goal5359_cell_mbr_author_like_queue_route_test tests.goal5358_author_like_radius_queue_reference_test tests.goal5357_author_rtdl_radius_trace_comparison_test tests.goal5356_route_radius_trace_metadata_test tests.goal5355_radius_trace_mapping_test tests.goal5354_radius_growth_schedule_test tests.goal5353_xhd_author_rt_option_surface_gate_test
```

Result:

```text
Ran 30 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

The next work should integrate this route variant into the hd_exec-compatible
wrapper behind an explicit internal route label, then run the same bounded trace
comparison through that wrapper.

After bounded wrapper integration, the next harder gate is a nonterminal author
trace case where `NumOutputPoints > 0` and `radius_growth_step` actually updates
the radius.

POD expectation:

```text
Goal5359 itself does not need POD.
POD is likely needed for OptiX/GPU validation and for Level-B/nonterminal
author trace comparison.
```
