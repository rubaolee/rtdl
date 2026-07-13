# Goal5376 Status-Machine Candidate Contract Result

Date: 2026-07-10

## Verdict

`completed_status_machine_candidate_contract__author_lb_parity_still_unresolved`

Goal5376 adds a generic RTDL telemetry contract for the current cell-MBR frontier
producer:

```text
rtdl.optix.cell_mbr_nearest_frontier_3d.status_machine_candidate_telemetry.v1
```

This is **not** explicit X-HD `-lb` support. It is a system-facing status-shaped
surface that lets the X-HD app compare current RTDL frontier behavior against the
Goal5374 author `-lb` oracle without hard-coding author semantics into RTDL core.

## What Changed

### 1. Generic runtime telemetry

`src/rtdsl/optix_runtime.py` now derives and returns:

```text
status_machine_telemetry_collected
status_machine_telemetry
native_memory_telemetry.status_machine_candidate_telemetry
```

The telemetry fields include:

- `active_in_queue_size`
- `raw_offload_rows_before_sort_reduce`
- `raw_offload_rows_author_width_bytes`
- `status_count_init`
- `status_count_offloading`
- `point_loop_early_break_count`
- `current_best_state_source`
- explicit claim guards:
  - `explicit_lb_support_claimed: false`
  - `row_count_parity_claimed: false`
  - `same_denominator_memory_claimed: false`

The contract is intentionally app-neutral:

```text
generic_cell_mbr_frontier_status_machine_candidate
```

It does not contain X-HD-specific names and does not encode author-specific
`loadBalanceProcessing` semantics.

### 2. Column front-door passthrough

`src/rtdsl/partner_continuations.py` now forwards:

```text
metadata.status_machine_telemetry_collected
metadata.status_machine_telemetry
```

from the native OptiX collector result to the public columnar front-door
metadata. This makes the telemetry visible to paper apps and future system
tests without app-specific hooks.

### 3. Goal5376 artifact

Generated:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5376_status_machine_candidate_contract.json
```

Key fields:

```text
status: rtdl_status_machine_candidate_contract_implemented__author_lb_row_parity_not_established
exit_label: status_machine_candidate_surface_ready__real_author_lb_mode_still_required
status_candidate_contract_ready: true
author_lb_row_parity_established: false
explicit_lb_support_authorized: false
```

The artifact preserves the Goal5374 author oracle:

```text
active_in_queue_size: 437645
offloading_size_rows: 27133990
raw_offload_rows_author_width_bytes: 217071920
status_count_init: 437645
status_count_offloading: 27133990
status_count_cmax2_mbr_abort: 0
status_count_point_loop_early_break: 0
```

It also preserves the Goal5375 best current RTDL candidate:

```text
best_candidate: goal5365_full_cover_lb256_behavior_gate_surface
best_candidate_rows: 24508120
absolute_row_delta: 2625870
row_count_parity: false
```

## What This Proves

Goal5376 proves:

1. RTDL now exposes a generic, app-neutral status-shaped telemetry surface for
   the current cell-MBR frontier producer.
2. The public Python/columnar front-door forwards that telemetry to callers.
3. The X-HD app can compare current RTDL status-shaped fields against the
   Goal5374 author `-lb` oracle without pretending the fields are equivalent.
4. The current route still does **not** establish author `-lb` row parity.

## What This Does Not Prove

Goal5376 does **not** prove:

- explicit X-HD `-lb` support;
- author RT-core algorithm parity;
- Figure 7 or Figure 11 reproduction;
- same-denominator memory parity;
- performance parity or any author/RTDL performance ratio;
- full X-HD paper reproduction;
- exact paper dataset reproduction.

## Remaining Semantic Gaps

The following author `-lb` semantics remain missing or only analogs:

```text
author cmin2/current-best restoration by in_q_idx
author cmax2 MBR abort status counter
author miss_queue append/count semantics
author loadBalanceProcessing sort/reduce feedback into later state
row-count parity against Goal5374 OffloadingSize
```

This is the next hard implementation target. The status candidate contract makes
the gap observable, but it does not close the gap.

## Validation

Commands run locally:

```text
py -m py_compile src/rtdsl/optix_runtime.py src/rtdsl/partner_continuations.py

py -m unittest \
  tests.goal5376_status_machine_candidate_telemetry_test \
  tests.goal5376_status_machine_candidate_contract_artifact_test \
  tests.goal5211_global_bound_early_break_contract_test \
  tests.goal5172_native_inline_nearest_frontier_test
```

Result:

```text
Ran 11 tests in 1.404s
OK
```

POD preflight also passed through the required wrapper:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

No full POD route probe is claimed for this goal. The remote workspace exists
but is not a git checkout, so the next POD step should explicitly sync/build the
changed files before using the new telemetry in a full route.

## Next Goal

Goal5377 should implement or probe a real RTDL status-machine mode against the
Goal5374 oracle. The minimum next gate is:

```text
active_in_queue_size == 437645
raw_offload_rows_before_sort_reduce == 27133990
raw_offload_rows_author_width_bytes == 217071920
status_count_init == 437645
status_count_offloading == 27133990
status_count_aborted / cmax2 / miss semantics explicitly accounted for
```

If the new mode cannot match those denominators, it must report the row deltas
and keep `explicit_lb_support_claimed=false`.
