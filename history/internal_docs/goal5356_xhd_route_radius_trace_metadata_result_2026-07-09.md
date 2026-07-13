# Goal5356 - X-HD Route Radius Trace Metadata

## Status

```text
implemented_review_pending
```

Exit label:

```text
route_radius_trace_metadata_ready__await_author_rtdl_trace_comparison
```

## Purpose

Goal5355 proved that available author `hd_exec` JSON radius transitions can be
replayed by the generic RTDL `radius_growth_step` helper. Goal5356 prepares the
RTDL side of the future comparison by adding **app-owned internal radius trace
metadata** to the X-HD cell-MBR route under an explicit flag.

This is still not author `tune_radius` support. The current RTDL route is a
single-pass cell-MBR route, not the author's iterative radius queue. Therefore
the emitted metadata is deliberately labeled:

```text
author_queue_semantics_aligned = false
author_trace_comparison_ready = false
route_uses_radius_growth_helper = false
```

## Code Changes

Updated:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py
```

Added:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5356_route_radius_trace_metadata.py
tests/goal5356_route_radius_trace_metadata_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5356_route_radius_trace_metadata.json
```

The new app-owned flag:

```text
--emit-radius-trace-metadata
```

When enabled on the cell-MBR route gate, the summary includes:

```text
radius_trace_metadata
```

When enabled through `run_xhd_rtdl_hd_exec.py`, the wrapper can carry that same
metadata in:

```text
RTDL.radius_trace_metadata
Running.Repeats[0].RTDLRadiusTrace
```

## Artifact

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5356_route_radius_trace_metadata.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.goal5356.route_radius_trace_metadata.v1
```

Status:

```text
route_radius_trace_metadata_available__single_pass_not_author_queue_aligned
```

The artifact runs a local bounded3d route probe:

```text
input_fixture = bounded3d_a.wkt -> bounded3d_b.wkt
backend = numpy
route = rtdl_cell_mbr_frontier_numpy_3d
direction_mode = directed-a-to-b
emit_radius_trace_metadata = true
hd_result = 2.0
point_count_a = 9
point_count_b = 8
grid_shape = [1,1,1]
```

Emitted trace metadata:

```text
status = single_pass_cell_mbr_radius_trace_metadata_available__author_queue_semantics_not_aligned
route_iteration_model = single_pass_cell_mbr_route_not_author_radius_loop
author_queue_semantics_aligned = false
author_trace_comparison_ready = false
route_uses_radius_growth_helper = false
```

First direction row:

```text
label = a_to_b
iteration = 1
radius = 3.3166247913554
num_input_points = 9
num_output_points = 9
input_count_semantics = source_point_count_before_single_pass_not_author_in_queue
output_count_semantics = frontier_row_count_after_single_pass_not_author_out_queue
```

## Fail-Closed Boundary

Goal5356 also checks that explicit author `-tune_radius adaptive` still fails
closed before route execution:

```text
explicit_tune_radius_status = unsupported_author_rt_options_fail_closed
explicit_author_rt_options = ["tune_radius"]
route_executed = false
```

This preserves the Goal5353 / Goal5354 boundary. The trace metadata flag does
not silently convert author `-tune_radius` into a supported option.

## Claim Boundary

Goal5356 does not claim:

```text
author tune_radius route mapping
author RT-core algorithm equivalence
Figure 8 reproduction
performance improvement
full X-HD paper reproduction
```

Allowed claim:

```text
The X-HD app-owned RTDL cell-MBR route can emit internal radius trace metadata
under an explicit diagnostic flag, and that metadata is correctly labeled as
single-pass / not author queue aligned.
```

Forbidden summaries:

```text
RTDL now supports author -tune_radius.
RTDL route radius trace matches author radius trace.
RTDL reproduces Figure 8.
Goal5356 proves author RT-core parity.
Goal5356 improves performance.
```

## Validation

Commands run:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5356_route_radius_trace_metadata.py --output Paper-reproduction-apps\x-hd-paper\results\xhd_goal5356_route_radius_trace_metadata.json

py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_goal5356_route_radius_trace_metadata.json

py -m unittest tests.goal5356_route_radius_trace_metadata_test tests.goal5355_radius_trace_mapping_test tests.goal5354_radius_growth_schedule_test tests.goal5353_xhd_author_rt_option_surface_gate_test
```

Result:

```text
Ran 21 tests OK
```

The local Python launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Next Work

Recommended next target:

```text
compare_author_and_rtdl_radius_trace_on_bounded_or_level_b_input
```

That next goal must decide whether the current single-pass route trace is
sufficient only as a negative/control row, or whether a route variant should
emit author-like radius/input/output iterations using the Goal5354 helper.

POD expectation:

```text
No POD is needed for Goal5356 review.
POD is likely needed for the next author-vs-RTDL trace comparison if it runs
author hd_exec and RTDL route traces on a bounded or Level-B input.
```
