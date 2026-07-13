# Goal5386 X-HD Author Trace V2 Patch Plan Result

Date: 2026-07-10

Status:

```text
implemented_review_pending
```

Exit label:

```text
author_trace_v2_patch_plan_ready__implementation_next
```

## Purpose

Goal5385 defined the stronger author trace v2 oracle needed for X-HD explicit
`-lb` parity work.  Goal5386 turns that schema into a fail-closed author-source
hook validation and dry-run patch plan.

This goal does not apply the author patch and does not run a POD route.  Its
job is narrower:

```text
Goal5385 required fields
-> concrete author source files
-> concrete hook anchors
-> field coverage matrix
-> implementation-ready patch plan
```

## Files Added

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5386_author_trace_v2_patch_plan.py
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5386_author_trace_v2_patch_plan.json
```

Tests:

```text
tests/goal5386_author_trace_v2_patch_plan_test.py
```

## Author Source State

The builder validated the current local author source tree:

```text
C:\Users\Lestat\AppData\Local\Temp\xhd-author-src
```

Validated author-only patch targets:

```text
src/hd_impl/hausdorff_distance_rt.h
src/rt/launch_parameters.h
src/rt/shaders/shaders_nn_uniform_grid.cu
```

Instrumentation marker:

```text
RTDL_GOAL5385_LB_STATUS_TRACE_V2
```

The patch plan deliberately targets the author tree only.  It does not patch
RTDL core.

## Hook Validation Result

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5386_author_trace_v2_patch_plan.json
```

Core result:

```text
all_hooks_found = true
all_required_fields_covered = true
missing_files = []
missing_hooks = []
uncovered_fields = []
```

The artifact records concrete line numbers for each source hook, including:

```text
launch_parameter_trace_fields       line 44   src/rt/launch_parameters.h
outer_iteration_scope               line 273  src/hd_impl/hausdorff_distance_rt.h
batch_scope_and_active_queue        line 299  src/hd_impl/hausdorff_distance_rt.h
cmin2_initial_state                 line 304  src/hd_impl/hausdorff_distance_rt.h
shader_cmax2_abort_status           line 89   src/rt/shaders/shaders_nn_uniform_grid.cu
shader_offload_append_stream        line 100  src/rt/shaders/shaders_nn_uniform_grid.cu
after_ray_launch_state              line 348  src/hd_impl/hausdorff_distance_rt.h
load_balance_processing_call        line 354  src/hd_impl/hausdorff_distance_rt.h
load_balance_cmin2_feedback         line 580  src/hd_impl/hausdorff_distance_rt.h
miss_and_completed_status_after_raygen line 200 src/rt/shaders/shaders_nn_uniform_grid.cu
json_iteration_emit                 line 376  src/hd_impl/hausdorff_distance_rt.h
```

## Field Coverage

Every Goal5385 required batch field is covered by at least one concrete hook:

```text
batch_index
iteration_index
radius
active_in_queue_size
cmax2_before_ray
cmax2_after_ray
cmax2_after_load_balance
cmin2_initial_hash
cmin2_after_ray_hash
cmin2_after_load_balance_hash
cmin2_sample_indices
cmin2_initial_samples
cmin2_after_ray_samples
cmin2_after_load_balance_samples
raw_offload_rows_before_sort_reduce
raw_offload_row_hash
raw_offload_row_sample_point_ids
raw_offload_row_sample_cell_ids
status_count_init
status_count_offloading
status_count_aborted
status_count_miss
status_count_completed
cmax2_mbr_abort_count
point_loop_early_break_count
load_balance_input_row_count
load_balance_group_count
load_balance_feedback_update_count
```

Examples:

```text
raw_offload_row_hash:
  launch_parameter_trace_fields
  shader_offload_append_stream
  json_iteration_emit

cmin2_after_load_balance_hash:
  load_balance_cmin2_feedback
  json_iteration_emit

load_balance_feedback_update_count:
  load_balance_processing_call
  load_balance_cmin2_feedback
  json_iteration_emit
```

## Validation

Generated artifact:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5386_author_trace_v2_patch_plan.py
```

Observed:

```text
all_hooks_found = true
all_required_fields_covered = true
exit_label = author_trace_v2_patch_plan_ready__implementation_next
```

Focused tests:

```text
py -m unittest \
  tests.goal5386_author_trace_v2_patch_plan_test \
  tests.goal5385_author_trace_v2_spec_test \
  tests.goal5384_multiround_status_requirements_test \
  tests.goal5384_multiround_active_query_status_test
```

Observed:

```text
Ran 16 tests in 3.188s
OK
```

The local Windows `py` launcher printed the known noisy message:

```text
Could not find platform independent libraries <prefix>
```

Tests still passed.

## Claim Boundary

Allowed:

```text
Goal5386 validates that the current author source has concrete hooks for all
Goal5385 author trace v2 required fields.
Goal5386 produces an implementation-ready dry-run patch plan.
The next author patch can be fail-closed against these anchors.
```

Not allowed:

```text
author v2 trace implemented;
author v2 trace executed on POD;
explicit -lb support;
row-count parity;
Figure 7 reproduction;
Figure 11 reproduction;
author RT-core algorithm parity;
RTDL/author performance ratio;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Interpretation

Goal5386 removes a concrete ambiguity in the `-lb` line: the stronger author
trace v2 oracle is no longer only a list of desired fields.  It is now mapped to
specific source hooks in the pinned author tree.

The next implementation step should be Goal5387:

```text
apply the app-owned author trace v2 patch;
build author hd_exec on POD;
run Dragon -> AsianDragon lb=256;
emit rtdl.goal5385.author.lb_status_trace.v2;
compare v2 counts with Goal5374 and preserve all no-claim boundaries.
```
