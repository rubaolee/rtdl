# Goal5396 X-HD v6 Remap No-Go

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5396 answers a narrow but important question:

```text
Can the current native v6 frontier collector be promoted to the Goal5395
native status-stream ABI by a post-hoc column remap?
```

Answer:

```text
No.
```

Exit label:

```text
v6_remap_no_go__implement_real_v7_or_keep_lb_fail_closed
```

This goal does not implement native v7. It prevents a fake v7 path: relabeling
v6 frontier rows would preserve the wrong denominator and still lack the
required transition/current-best/feedback semantics.

## Files

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5396_v6_remap_no_go.py
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5396_v6_remap_no_go.json
```

Tests:

```text
tests/goal5396_v6_remap_no_go_test.py
```

## Author Oracle

From Goal5387:

```text
active_count = 437,645
raw_offload_rows_before_sort_reduce = 27,133,990
rows_per_active = 62
raw_offload_row_hash = 4333109858711462591
status_count_offloading = 27,133,990
feedback_update_count = 294
```

## Known RTDL Surfaces

From Goal5392:

```text
current bridge rows = 2,188,225 = 5 * active_count
raw kind2 rows = 21,006,960 = 48 * active_count
full-cover rows = 24,508,120 = 56 * active_count
overcount rows = 304,981,889 ~= 696.87 * active_count
```

No known RTDL surface has row-count parity or hash parity:

```text
any_surface_has_row_count_parity = false
any_surface_has_hash_parity = false
```

The closest v6-like surface is still short:

```text
author rows = 27,133,990
best v6-like rows = 24,508,120
delta = 2,625,870 = 6 * active_count
```

## Why v6 Remap Is Rejected

A v6 remap would only relabel existing rows. It would not:

```text
change denominator;
add the missing 6 rows per active query;
add transition phase semantics;
add feedback semantics;
add current-best before/after per status row.
```

Artifact decision:

```text
v6_column_remap_authorized = false
native_status_stream_backend_implemented_by_goal5396 = false
explicit_lb_remains_fail_closed = true
real_v7_backend_required = true
```

## Goal5395 ABI Gap Carried Forward

Goal5396 carries forward the Goal5395 audit:

```text
contract = generic_active_query_status_stream_native_abi_v1
current_v6_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6
current_surface_is_single_launch_frontier_probe = true
current_surface_satisfies_goal5394_native_probe = false
existing_native_v6_is_sufficient = false
```

Still missing:

```text
active_queue_index
source_id
status_code
transition_phase_code
current_best_before_sq
current_best_after_sq
```

Still missing semantically:

```text
multi-round feedback state
transition_phase_code
current_best_before_sq per status row
current_best_after_sq per status row
miss/completed/aborted row counts from the same native status stream
feedback update count or explicit not-applicable evidence from the native stream
```

## Verification

POD preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Artifact build:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5396_v6_remap_no_go.py
```

Focused tests:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5396_v6_remap_no_go_test tests.goal5395_native_status_stream_abi_gate_test tests.goal5394_full_cover_delta_status_probe_test
```

Observed:

```text
Ran 12 tests in 4.925s
OK
```

Compile check:

```text
py -m py_compile Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5396_v6_remap_no_go.py tests\goal5396_v6_remap_no_go_test.py
```

Observed:

```text
no compile failure
```

The Windows environment may print:

```text
Could not find platform independent libraries <prefix>
```

That warning was non-fatal.

## Claim Boundary

Allowed claim:

```text
Goal5396 rejects v6 column-remap as a valid native status-stream backend and
keeps explicit -lb fail-closed until a real generic v7 backend exists.
```

Not claimed:

```text
native_backend_completion_claimed = false
existing_native_v6_parity_claimed = false
v6_column_remap_claimed_sufficient = false
explicit_lb_support_claimed = false
row_count_parity_claimed = false
hash_sample_parity_claimed = false
figure7_reproduction_claimed = false
figure11_reproduction_claimed = false
same_denominator_memory_claimed = false
author_rt_core_algorithm_parity_claimed = false
performance_ratio_claimed = false
exact_paper_dataset_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
```

## Next Work

Recommended next goal:

```text
Goal5397
```

Goal5397 must not be another wrapper/remap. It must either:

```text
1. Implement a real generic native active-query status-stream backend emitted
   at traversal/status transition points, with current-best before/after,
   transition phase, and feedback/miss/completed/aborted telemetry.

2. Keep explicit -lb fail-closed if a real implementation would require
   X-HD-specific constants or author-only status logic in RTDL core/native.
```

POD is required for Goal5397 if native OptiX code changes or full
Dragon -> AsianDragon status-stream gates are run.
