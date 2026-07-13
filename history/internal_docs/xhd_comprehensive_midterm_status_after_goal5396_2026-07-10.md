# X-HD Comprehensive Midterm Status After Goal5396

Date: 2026-07-10

## Current Status

```text
level_b_scalar_strong__generic_system_extraction_real__explicit_lb_v6_remap_rejected__real_v7_required__full_paper_not_complete
```

This report supersedes:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5395_2026-07-10.md
```

as the current working snapshot.

## Executive Summary

X-HD reproduction has strong Level-B scalar evidence and real RTDL generic
system extraction. The remaining hard functional gap is explicit X-HD `-lb`
status-stream parity.

Goal5394 pinned the closest known RTDL denominator surface:

```text
full-cover = 24,508,120 rows = 56 * active_count
```

Goal5395 added the generic native status-stream ABI and proved current native
v6 is insufficient.

Goal5396 now closes the unsafe shortcut:

```text
v6 column remap is rejected.
```

Therefore, the only valid implementation path is a real generic native v7
active-query status-stream backend emitted at traversal/status transition
points, or explicit `-lb` must remain fail-closed.

## Current Evidence Levels

```text
Level A bounded same-input correctness: complete and reviewed through Goal5126
Level B same-source public representative scalar route: strong
Level C exact paper dataset reproduction: not complete
Level D figure/performance reproduction: not complete
Level E explicit -lb / RT-core parity: not complete
```

## Strongest Scalar Evidence

Public Stanford Dragon -> HappyBuddha Level-B route:

```text
source points = 437,645
target points = 543,652
author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
absolute diff   ~= 2.38e-9
```

Current fast scalar caveat:

```text
per_source_witness_exact = false
early-aborted sources = 409,376 / 437,645
```

This is an exact directed-Hausdorff scalar result under the max-nearest
contract, not exact per-source witness reproduction.

## Explicit `-lb` Author Oracle

From Goal5387 author trace v2:

```text
active_count = 437,645
raw_offload_rows_before_sort_reduce = 27,133,990
rows_per_active = 62
raw_offload_row_hash = 4333109858711462591
status_count_offloading = 27,133,990
feedback_update_count = 294
```

## Known RTDL Denominator Surfaces

From Goal5392 / Goal5396:

```text
current bridge rows = 2,188,225 = 5 * active_count
raw kind2 rows = 21,006,960 = 48 * active_count
full-cover rows = 24,508,120 = 56 * active_count
overcount rows = 304,981,889 ~= 696.87 * active_count
```

No known RTDL surface has row-count parity or hash parity.

Closest known surface:

```text
full-cover rows = 24,508,120 = 56 * active_count
author rows = 27,133,990 = 62 * active_count
missing rows = 2,625,870 = 6 * active_count
```

## Goal5394 Status

Goal5394 is implemented / review pending.

It demonstrates only shape capability:

```text
generic_active_query_multiround_status_reference_v1
base rows per active = 56
delta rows per active = 6
target rows per active = 62
app_semantics = none
```

It does not implement native code and does not prove author parity.

## Goal5395 Status

Goal5395 is implemented / review pending.

It adds:

```text
generic_active_query_status_stream_native_abi_v1
```

and audits current v6:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6 exists
current_surface_is_single_launch_frontier_probe = true
current_surface_satisfies_goal5394_native_probe = false
existing_native_v6_is_sufficient = false
```

## Goal5396 Status

Goal5396 is implemented / review pending.

It rejects v6 column-remap:

```text
v6_column_remap_authorized = false
native_status_stream_backend_implemented_by_goal5396 = false
explicit_lb_remains_fail_closed = true
real_v7_backend_required = true
```

Reason:

```text
A v6 remap would only relabel existing rows.
It would not change the 56x denominator.
It would not add the missing 6 rows per active.
It would not add transition phase semantics.
It would not add feedback semantics.
It would not add current-best before/after per status row.
```

## Validation

POD preflight:

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
POD_OK
45c502cfccb5
NVIDIA RTX 4000 Ada Generation, 550.127.05
```

Focused tests:

```text
$env:PYTHONPATH='src'; py -m unittest tests.goal5396_v6_remap_no_go_test tests.goal5395_native_status_stream_abi_gate_test tests.goal5394_full_cover_delta_status_probe_test
Ran 12 tests OK
```

## What Remains

The next real implementation goal is:

```text
Goal5397
```

Goal5397 must either:

```text
implement a real generic native active-query status-stream backend emitted at
traversal/status transition points;
```

or:

```text
keep explicit -lb fail-closed if implementation requires X-HD-specific
constants or author-only logic.
```

It must not:

```text
wrap or relabel v6 frontier rows;
hard-code 6 missing rows per active;
hard-code 62 author rows per active;
claim explicit -lb before row/hash or deterministic sample parity;
place X-HD option/figure semantics into RTDL core or native code.
```

## POD Expectation

Goal5397 requires POD if native OptiX code is changed or full status-stream
parity gates are run. Use only:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

## Allowed Summary

```text
X-HD has strong Level-B scalar correctness and real generic system extraction.
The explicit -lb line is now narrowed to one honest path: current v6 cannot be
remapped into the required status-stream backend, so a real generic native v7
status stream is required, or -lb remains fail-closed. Full paper reproduction
is still not complete.
```

## Forbidden Summaries

Do not say:

```text
X-HD full paper reproduction is complete.
RTDL supports explicit -lb.
v6 can satisfy the native status-stream ABI by remapping columns.
Goal5396 implements native v7.
The missing 6x-active delta is solved.
RTDL has Figure 7/11 or same-denominator performance parity.
```
