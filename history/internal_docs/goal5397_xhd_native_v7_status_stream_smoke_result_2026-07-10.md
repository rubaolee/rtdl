# Goal5397: Native v7 Active-Query Status Stream Smoke Result

Date: 2026-07-10

## Verdict

```text
native_v7_status_stream_smoke_passed__full_parity_pending
```

## Purpose

Goal5396 rejected the unsafe shortcut of remapping existing native v6 frontier
rows into the new active-query status-stream ABI. Goal5397 therefore starts the
real native v7 path:

```text
rtdl_optix_collect_active_query_status_stream_3d_v1
```

The goal of this step is deliberately narrow:

```text
prove a real app-neutral native v7 status-stream symbol builds on POD and emits
status rows through the Python front door.
```

This is **not** a full X-HD `-lb` implementation and not a row/hash parity gate.

## Implemented Changes

### Native ABI / Prelude

File:

```text
src/native/optix/rtdl_optix_prelude.h
```

Added:

```text
RtdlActiveQueryStatusStreamRow
rtdl_optix_collect_active_query_status_stream_3d_v1
```

The row schema is app-neutral:

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

### Native Workload Plumbing

File:

```text
src/native/optix/rtdl_optix_workloads.cpp
```

Added optional `status_rows_out` plumbing to the generic 3-D cell-MBR frontier
collector. When a row is emitted, a matching status row is written with:

```text
active_queue_index = query launch index
query_row_id = query launch index
source_id = query point id
cell_id = intersected cell id
status_code = frontier kind
transition_phase_code = frontier kind
current_best_before_sq = status best before row emission
current_best_after_sq = status best after row emission
```

This is a first v7 status-row emission point. It intentionally does **not**
claim to implement the author's full multi-round `-lb` state machine.

### C ABI

File:

```text
src/native/optix/rtdl_optix_api.cpp
```

Added:

```text
extern "C" int rtdl_optix_collect_active_query_status_stream_3d_v1(...)
```

The function calls the existing generic native 3-D cell-MBR collector with
status-row output enabled and returns the status-stream columns.

### Python Front Door

Files:

```text
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
```

Added and exported:

```text
collect_active_query_status_stream_3d_optix(...)
```

Metadata boundary:

```text
contract = generic_active_query_status_stream_native_abi_v1
native_backend_complete = false
explicit_app_option_support_claimed = false
claim_boundary = not application option support, not row/hash parity, not paper performance
```

### POD Smoke Script

File:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5397_native_status_stream_smoke.py
```

This script runs a synthetic two-query / two-cell status-stream smoke. It does
not use X-HD paper inputs and does not compare against author `hd_exec`.

## Evidence

### Local Focused Tests

Command:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5397_native_status_stream_frontdoor_test tests.goal5396_v6_remap_no_go_test tests.goal5395_native_status_stream_abi_gate_test
```

Result:

```text
Ran 14 tests in 2.807s
OK
```

Notes:

```text
The local Python warning "Could not find platform independent libraries
<prefix>" is the known local environment noise and did not fail tests.
```

### Python Compile Check

Command:

```text
py -m py_compile src\rtdsl\optix_runtime.py src\rtdsl\__init__.py Paper-reproduction-apps\x-hd-paper\scripts\run_xhd_goal5397_native_status_stream_smoke.py
```

Result:

```text
no compile failure
```

### POD Preflight

Command:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Result:

```text
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

### POD Focused Test

Command:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
python3 -m unittest tests.goal5397_native_status_stream_frontdoor_test
```

Result:

```text
Ran 5 tests in 0.497s
OK
```

### POD Native Build

Command:

```text
cd /root/rtdl_goal5093
make build-optix
```

Result:

```text
build/librtdl_optix.so built successfully
```

### POD Native v7 Smoke

Command:

```text
cd /root/rtdl_goal5093
export PYTHONPATH=src
export RTDL_OPTIX_LIB=/root/rtdl_goal5093/build/librtdl_optix.so
python3 Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5397_native_status_stream_smoke.py
```

Local artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5397_native_status_stream_smoke_pod.json
```

Key fields:

```text
matched = true
status = native_v7_status_stream_smoke_passed
native_generic_symbol = rtdl_optix_collect_active_query_status_stream_3d_v1
contract = generic_active_query_status_stream_native_abi_v1
valid_count = 4
attempted_count = 4
status_codes = [2]
source_ids = [100, 101]
cell_ids = [10, 11]
```

Claim boundary in artifact:

```text
native_v7_symbol_smoke_claimed = true
explicit_lb_support_claimed = false
row_count_parity_claimed = false
hash_sample_parity_claimed = false
figure7_reproduction_claimed = false
figure11_reproduction_claimed = false
performance_ratio_claimed = false
exact_paper_dataset_reproduction_claimed = false
full_xhd_paper_reproduction_claimed = false
```

## What This Proves

```text
1. The v7 native symbol is present in source and exported by a POD-built OptiX
   backend.
2. The Python front door can call the v7 symbol.
3. The native backend can emit app-neutral active-query status rows on a
   synthetic fixture.
4. The row schema and metadata match the Goal5395 ABI contract shape.
5. The work is not merely a v6 column remap in Python.
```

## What This Does Not Prove

```text
1. It does not prove explicit X-HD -lb support.
2. It does not prove row-count parity against Goal5387 author trace v2.
3. It does not prove hash/sample parity.
4. It does not explain or close the missing 6 rows per active query.
5. It does not reproduce Figure 7 or Figure 11.
6. It does not authorize any performance ratio.
7. It does not complete full X-HD paper reproduction.
```

## Known Limitation

The first v7 implementation emits status rows at the current native emitted-row
points. This is a real native status stream, but it may still inherit v6-like
denominator behavior.

Therefore the next gate must compare against the Goal5387 author trace v2
oracle before any `-lb` claim:

```text
author rows = 27,133,990
author raw hash = 4333109858711462591
feedback update count = 294
```

## Historical Test Amendment

The Goal5395 historical ABI test originally asserted:

```text
future_symbol_already_present = false
```

That was correct when Goal5395 was written, but Goal5397 now intentionally adds
the future symbol. The test was amended to keep Goal5395 as an ABI/gap gate
without requiring the old "future symbol absent" snapshot to block the new
implementation goal.

This amendment does not promote Goal5395 to native backend completion.

## Next Recommended Goal

```text
Goal5398: native v7 status-stream parity gate against Goal5387 author trace v2.
```

Goal5398 should compare:

```text
active_count
row_count
status_count_offloading
raw row hash or deterministic samples
transition phase fields
current-best before/after fields
feedback / miss / completed / aborted telemetry
```

Exit labels:

```text
native_v7_status_stream_author_trace_parity_passed
native_v7_status_stream_denominator_mismatch__lb_remains_fail_closed
native_v7_status_stream_semantic_gap__new_generic_state_machine_required
```
