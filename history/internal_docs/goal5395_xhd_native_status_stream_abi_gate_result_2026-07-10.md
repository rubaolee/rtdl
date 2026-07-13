# Goal5395 X-HD Native Status-Stream ABI Gate

Date: 2026-07-10

## Verdict

```text
implemented_review_pending
```

## Summary

Goal5395 turns the Goal5394 native probe requirements into a public generic
RTDL ABI contract and audits whether the current native surface can satisfy it.

Result:

```text
status = native_status_stream_abi_contract_ready__native_backend_not_implemented
exit   = native_status_stream_abi_gate_ready__implement_v7_or_fail_closed_next
```

Goal5395 does **not** implement native backend code and does **not** claim
explicit `-lb` support. It establishes a generic contract for a future native
active-query status stream and shows that the current v6 native frontier probe
is insufficient for the Goal5394 target.

## Files

Implementation:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
```

Builder:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5395_native_status_stream_abi_gate.py
```

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5395_native_status_stream_abi_gate.json
```

Tests:

```text
tests/goal5395_native_status_stream_abi_gate_test.py
```

## Public Generic ABI Added

Goal5395 adds the following app-neutral RTDL exports:

```text
ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT
ACTIVE_QUERY_STATUS_STREAM_NATIVE_ROW_SCHEMA
ACTIVE_QUERY_STATUS_STREAM_NATIVE_TELEMETRY_SCHEMA
active_query_status_stream_native_abi_contract()
validate_active_query_status_stream_native_abi_contract()
```

Contract id:

```text
generic_active_query_status_stream_native_abi_v1
```

Reference contract:

```text
generic_active_query_multiround_status_reference_v1
```

The contract is intentionally non-executable:

```text
executable = false
app_generic = true
explicit_app_option_support_claimed = false
```

## Required Row Schema

The future native status stream must expose:

```text
active_queue_index
query_row_id
source_id
cell_id
status_code
transition_phase_code
current_best_before_sq
current_best_after_sq
```

These names are generic active-query status fields. They do not encode X-HD,
figure numbers, author option names, or paper-specific semantics.

## Required Telemetry Schema

The future backend must also provide:

```text
raw_offload_rows_before_sort_reduce
raw_offload_row_hash_or_sample_rows
status_count_offloading
feedback_update_count_or_not_applicable
miss_count
completed_count
aborted_count
```

This is the minimum telemetry needed to compare against the Goal5387 author
trace v2 oracle without using a row-count-only shortcut.

## Goal5394 Target Carried Forward

Goal5395 pins the Goal5394 target:

```text
author rows      = 27,133,990 = 62 * active_count
full-cover rows  = 24,508,120 = 56 * active_count
missing rows     =  2,625,870 =  6 * active_count
```

The artifact keeps:

```text
full_cover_is_correctness_claim = false
```

Interpretation:

```text
Full-cover remains a useful target surface, not correctness.
The 6x-active delta must not be hard-coded.
The 62x-active author denominator must not be hard-coded.
```

## Current Native Surface Audit

Current latest native probe:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6
```

Audit result:

```text
latest_symbol_present_in_python_and_native_sources = true
current_surface_is_single_launch_frontier_probe = true
current_surface_satisfies_goal5394_native_probe = false
```

Planned future symbol is not present:

```text
rtdl_optix_collect_active_query_status_stream_3d_v1
future_symbol_already_present = false
```

The v6 surface exposes frontier rows such as:

```text
frontier_kind_code
query_row_id
query_point_id
cell_id
point_begin_offset
point_count
min_distance
max_distance
nearest_distance
nearest_item_id
```

But it lacks required status-stream fields:

```text
active_queue_index
source_id
status_code
transition_phase_code
current_best_before_sq
current_best_after_sq
```

It also lacks required semantics:

```text
multi-round feedback state
transition_phase_code
current_best_before_sq per status row
current_best_after_sq per status row
miss/completed/aborted row counts from the same native status stream
feedback update count or explicit not-applicable evidence from the native stream
```

Conclusion:

```text
existing_native_v6_is_sufficient = false
```

## Verification

Artifact build:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5395_native_status_stream_abi_gate.py
```

Focused tests:

```text
py -m unittest tests.goal5395_native_status_stream_abi_gate_test tests.goal5394_full_cover_delta_status_probe_test tests.goal5384_multiround_active_query_status_test
```

Observed:

```text
Ran 11 tests in 2.741s
OK
```

Compile check:

```text
py -m py_compile src\rtdsl\active_query_status.py src\rtdsl\__init__.py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5395_native_status_stream_abi_gate.py
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
Goal5395 adds a generic native active-query status-stream ABI contract and
audits that the current v6 native frontier probe cannot satisfy it.
```

Not claimed:

```text
native_backend_completion_claimed = false
existing_native_v6_parity_claimed = false
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
Goal5396
```

Goal5396 should choose one of two paths:

```text
1. Implement a new generic native active-query status-stream backend matching
   generic_active_query_status_stream_native_abi_v1, then run POD row/hash or
   deterministic sample gates against the Goal5387 author trace v2 oracle.

2. Fail-close explicit load-balance support if matching the author trace would
   require X-HD-specific constants or paper-only status logic in RTDL core/native.
```

Goal5396 requires POD if it changes native OptiX code or runs the full
Dragon -> AsianDragon status-stream parity gate. Use only:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

## Exit Label

```text
native_status_stream_abi_gate_ready__implement_v7_or_fail_closed_next
```
