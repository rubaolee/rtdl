# Goal5372 - X-HD Author Shader Status-Machine Gap Matrix

Date: 2026-07-09

Status: `implemented_review_pending`

## Verdict Label

```text
author_shader_status_machine_gap_matrix_ready__implementation_or_author_instrumentation_next
```

Exit label:

```text
status_machine_requirements_ready__lb_support_still_unauthorized
```

## Purpose

Goals5363-5371 narrowed the `-lb` / heavy-cell offload problem from "value
correctness" to a denominator-alignment problem:

```text
author lb256 OffloadingSize = 27,133,990
RTDL author-radius inline count-only kind2 = 21,006,960
RTDL author-radius no-inline raw kind2     = 304,981,889
```

Goal5372 pins the author shader payload/status-machine semantics that control
that denominator and maps them to the current RTDL gaps. This goal does not
implement explicit `-lb` support.

## Files

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5372_author_shader_status_machine_gap.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5372_author_shader_status_machine_gap.json
tests/goal5372_author_shader_status_machine_gap_test.py
```

## Author Source Evidence

Checked source files:

```text
C:/Users/Lestat/AppData/Local/Temp/xhd-author-src/src/rt/shaders/shaders_nn_uniform_grid.cu
C:/Users/Lestat/AppData/Local/Temp/xhd-author-src/src/hd_impl/hausdorff_distance_rt.h
```

The artifact verifies the following source facts:

```text
ShaderStatus = kInit | kOffloading | kAborted
payload_0 = in_q_idx
payload_1 = n_hits
payload_2 = n_compared_pairs
payload_3 = status
payload_4/5 = cmin2

radius/cmin2 prune exists:
  min_dist2 > radius^2 OR min_dist2 >= cmin2

cmax2 MBR abort exists:
  max_dist2 <= cmax2 -> update cmin2, set kAborted, terminate ray

heavy-cell offload append exists:
  np_in_cell > processing_threshold -> append (in_q_idx, cell_id),
  set kOffloading, return

point-loop early break exists:
  dist2 <= cmax2 -> set kAborted, terminate ray

raygen post-status mapping exists:
  kAborted -> cmin2[i] = INVALID_DISTANCE
  kOffloading -> cmin2[i] = cmin2
  valid complete -> atomicMax(cmax2, cmin2)
  no finite cmin2 -> miss_queue append

loadBalanceProcessing restores shader cmin2 by idx_in_queue and can update
global cmax2 after processing offloaded cells.
```

## Gap Matrix

Goal5372 records six required semantics for the next valid `-lb` denominator
gate:

```text
active in_queue index namespace
dynamic per-source cmin2
cmax2 abort status
heavy-cell offload append
loadBalanceProcessing grouping
miss queue
```

Current RTDL status:

```text
active in_queue index namespace:
  missing for Dragon -> AsianDragon lb trace

dynamic per-source cmin2:
  bounded state shape exists, but large lb trace cmin2 is missing

cmax2 abort status:
  existing global-bound flag does not fire in Goal5371

heavy-cell offload append:
  generic kind2 counts exist, but denominator does not match

loadBalanceProcessing grouping:
  not represented in current count-only probe

miss queue:
  not present in current lb count probes
```

## Next Gate Contract

Next gate:

```text
author_shader_status_machine_lb_trace
```

Minimum fields:

```text
active_in_queue_size
raw_offload_rows_before_sort_reduce
raw_offload_rows_author_width_bytes
status_count_init
status_count_offloading
status_count_aborted
miss_queue_count
cmax2_mbr_abort_count
point_loop_early_break_count
current_best_state_source
row_count_parity_against_author_offloading_size
```

Implementation options:

```text
1. Build a generic RTDL experimental status-machine probe over cell-MBR
   traversal.

2. Instrument/regenerate author to dump raw offload rows and per-source
   status/cmin2 oracle, then compare RTDL against that stronger oracle.
```

Success exit:

```text
author_status_machine_lb_denominator_compared
```

Failure exit:

```text
author_status_machine_requires_deeper_instrumentation
```

## Validation

Commands:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5372_author_shader_status_machine_gap.py
py -m unittest tests.goal5372_author_shader_status_machine_gap_test tests.goal5371_inline_global_bound_lb_probe_test tests.goal5369_lb_queue_state_requirements_test tests.goal5370_author_like_queue_state_reference_test
```

Result:

```text
Ran 12 tests OK
```

## Claim Boundary

Allowed:

```text
Goal5372 pins author shader/status-machine semantics and defines the next
author-status-machine lb trace gate.
```

Not authorized:

```text
explicit -lb support
row-count parity
same-denominator memory parity
Figure 7 reproduction
Figure 11 reproduction
author RT-core algorithm parity
RTDL/author performance ratio
exact paper dataset reproduction
full X-HD paper reproduction
```

## Next Work

Implement or instrument the `author_shader_status_machine_lb_trace` gate. Do
not continue scalar-radius, raw-kind2, or existing global-bound probes as
explanations for `OffloadingSize`.
