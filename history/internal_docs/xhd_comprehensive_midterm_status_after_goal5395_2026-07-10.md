# X-HD Comprehensive Midterm Status After Goal5395

Date: 2026-07-10

## Current Status

```text
level_b_scalar_strong__generic_system_extraction_real__explicit_lb_abi_gate_ready__native_status_stream_not_implemented__full_paper_not_complete
```

This report supersedes the earlier after-Goal5393 midterm status for the current
working state. The earlier report remains useful historical context:

```text
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5393_2026-07-10.md
```

## One-Sentence Summary

X-HD has strong same-source representative scalar evidence and real RTDL generic
system extraction, but full paper reproduction is not complete because exact
paper inputs and explicit `-lb` native status-stream parity remain unresolved.

## Top-Level Goal

The intended end state is:

```text
An X-HD paper reproduction app where RTDL/Python replaces the author C++/CUDA/
OptiX route as far as evidence permits, while preserving RTDL as a generic
language/system rather than turning core into an X-HD-specific codebase.
```

The project must keep these levels separate:

```text
Level A: bounded same-input correctness
Level B: same-source representative public-input correctness
Level C: exact paper dataset reproduction
Level D: figure/performance reproduction
Level E: author RT-core algorithm parity
```

Current state:

```text
Level A: complete and reviewed through Goal5126
Level B: strong for public Dragon -> HappyBuddha scalar route
Level C: not complete; exact paper inputs unavailable
Level D: not complete; no same-denominator performance ratio authorized
Level E: not complete; explicit -lb status-stream parity unresolved
```

## What Is Complete

### Bounded Same-Input X-HD

The bounded same-input line is complete and externally reviewed through
Goal5126:

```text
author and RTDL agree on directed Hausdorff value for bounded 2D/3D fixtures
directed-vs-symmetric ambiguity closed by an asymmetric fixture
status can be called bounded same-input value reproduction, not full paper reproduction
```

### Generic System Extraction

Goals5127 and 5128 extract the X-HD route shape into generic nearest/witness/
max-nearest components:

```text
pairwise_l2_distance_candidate_rows
nearest_witness
max_nearest_distance_witness
```

Hausdorff remains an app-level composition. The generic helpers have a
non-Hausdorff consumer, so the extraction is a genuine RTDL system improvement
rather than app-only code.

### Public Dragon -> HappyBuddha Level-B Scalar Route

Current strongest Level-B line:

```text
source = Stanford Dragon public PLY
target = Stanford HappyBuddha public PLY
source points = 437,645
target points = 543,652
author HDResult = 0.12572988867759705
RTDL HDResult   = 0.12572988629271128
absolute diff   ~= 2.38e-9
```

This is strong same-source representative scalar evidence. It is not exact
paper input reproduction because the paper-input byte identity is not proven.

### Fast Scalar Route

Best current scalar route facts:

```text
Goal5211 fresh route ~= 0.849s
Goal5211 explicit-warm route ~= 0.362s
Goal5212 fresh full total including input load ~= 1.531s
Goal5212 explicit-warm measured case total ~= 0.288s
```

Important caveat:

```text
per_source_witness_exact = false
early-aborted sources = 409,376 / 437,645
```

Therefore this route is an exact directed-Hausdorff scalar route under the
max-nearest contract, not an exact per-source witness route.

## Current Hard Problem

The current active hard problem is explicit X-HD `-lb` status-stream denominator
parity.

The author trace v2 oracle from Goal5387 reports:

```text
active_count = 437,645
raw_offload_rows_before_sort_reduce = 27,133,990
rows_per_active = 62
raw_offload_row_hash = 4333109858711462591
status_count_offloading_append = 27,133,990
feedback_update_count = 294
```

Current RTDL surfaces do not match this denominator:

```text
Goal5390 current RTDL bridge rows = 2,188,225 = 5 * active_count
Goal5392 default/inline raw kind2 rows = 21,006,960 = 48 * active_count
Goal5392 full-cover lb256 surface rows = 24,508,120 = 56 * active_count
Goal5393 selected full-cover as closest surface, but not correctness
```

The current missing aggregate delta is:

```text
author target rows = 27,133,990 = 62 * active_count
full-cover rows    = 24,508,120 = 56 * active_count
missing rows       =  2,625,870 =  6 * active_count
```

## Goal5394 Completed

Goal5394 is implemented / review pending.

Files:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5394_full_cover_delta_status_probe.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5394_full_cover_delta_status_probe.json
tests/goal5394_full_cover_delta_status_probe_test.py
history/internal_docs/goal5394_xhd_full_cover_delta_status_probe_result_2026-07-10.md
history/internal_docs/call_for_review_goal5394_xhd_full_cover_delta_status_probe_2026-07-10.md
```

Goal5394 proves only that the generic multi-round active-query status reference
can represent the required row shape:

```text
contract = generic_active_query_multiround_status_reference_v1
app_semantics = none
base rows per active = 56
delta rows per active = 6
target rows per active = 62
```

It does not prove author parity or native backend completion.

Focused tests:

```text
py -m unittest tests.goal5394_full_cover_delta_status_probe_test tests.goal5393_lb_status_stream_target_design_test tests.goal5392_lb_denominator_surface_reconciliation_test
Ran 13 tests OK
```

## Goal5395 Completed

Goal5395 is implemented / review pending.

Files:

```text
src/rtdsl/active_query_status.py
src/rtdsl/__init__.py
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5395_native_status_stream_abi_gate.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5395_native_status_stream_abi_gate.json
tests/goal5395_native_status_stream_abi_gate_test.py
history/internal_docs/goal5395_xhd_native_status_stream_abi_gate_result_2026-07-10.md
history/internal_docs/call_for_review_goal5395_xhd_native_status_stream_abi_gate_2026-07-10.md
```

Goal5395 adds the app-neutral public ABI contract:

```text
generic_active_query_status_stream_native_abi_v1
```

Public RTDL exports:

```text
ACTIVE_QUERY_STATUS_STREAM_NATIVE_ABI_CONTRACT
ACTIVE_QUERY_STATUS_STREAM_NATIVE_ROW_SCHEMA
ACTIVE_QUERY_STATUS_STREAM_NATIVE_TELEMETRY_SCHEMA
active_query_status_stream_native_abi_contract()
validate_active_query_status_stream_native_abi_contract()
```

The contract requires a future native backend to expose generic status-stream
rows:

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

and telemetry:

```text
raw_offload_rows_before_sort_reduce
raw_offload_row_hash_or_sample_rows
status_count_offloading
feedback_update_count_or_not_applicable
miss_count
completed_count
aborted_count
```

Goal5395 also audits the current v6 native surface:

```text
current symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v6
current_surface_is_single_launch_frontier_probe = true
current_surface_satisfies_goal5394_native_probe = false
future v7 symbol present = false
existing_native_v6_is_sufficient = false
```

Focused tests:

```text
py -m unittest tests.goal5395_native_status_stream_abi_gate_test tests.goal5394_full_cover_delta_status_probe_test tests.goal5384_multiround_active_query_status_test
Ran 11 tests OK
```

Compile check:

```text
py -m py_compile src\rtdsl\active_query_status.py src\rtdsl\__init__.py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_goal5395_native_status_stream_abi_gate.py
no compile failure
```

## What Is Not Complete

Do not claim:

```text
full X-HD paper reproduction
exact paper dataset reproduction
Figure 7 or Figure 11 reproduction
same-denominator performance ratio
same-denominator memory comparison
author RT-core algorithm parity
explicit -lb support
row/hash parity for the explicit lb status stream
native status-stream backend completion
```

## Why This Is Not Full Paper Reproduction Yet

Three blockers remain.

1. Exact paper inputs:

```text
The current Dragon -> HappyBuddha evidence uses public Stanford PLY files.
It matches the author rerun HDResult closely, but exact paper input byte identity
is not proven.
```

2. Explicit `-lb`:

```text
The author explicit -lb trace emits 62 rows per active query.
The closest current RTDL surface emits 56 rows per active query.
The missing 6 rows per active remain unexplained at row/hash parity level.
```

3. Native status-stream backend:

```text
Goal5395 defines the needed ABI, but the backend does not exist yet.
The existing v6 native frontier probe is insufficient.
```

## Next Planned Work

### Goal5396

Goal5396 should choose one of two outcomes:

```text
Implement a generic native active-query status-stream backend matching
generic_active_query_status_stream_native_abi_v1.

or

Fail-close explicit -lb support if matching the author status stream requires
X-HD-specific constants or author-only status logic.
```

Goal5396 requires POD if it changes native OptiX code or runs full
Dragon -> AsianDragon parity gates.

### Goal5396 Success Criteria

The native backend path must:

```text
emit generic status rows, not X-HD-specific rows;
compare row count against 27,133,990;
compare raw hash or deterministic sample rows when row schemas are comparable;
compare offloading status count;
provide feedback update count or explicit not-applicable evidence;
provide miss/completed/aborted counts;
avoid hard-coding 6 or 62 rows per active;
keep all claim boundaries false until evidence supports them.
```

### Goal5396 Failure Criteria

Fail-close if:

```text
row/hash parity requires hard-coded author constants;
the needed state machine is paper-specific rather than generic active-query
status-stream behavior;
native implementation would place X-HD option or figure semantics in RTDL core;
POD evidence cannot reproduce row/hash or deterministic sample movement toward
the author trace.
```

## POD Use Expectation

No POD was required for Goal5394 or Goal5395 because they are artifact/spec/API
gates and local tests suffice.

POD is expected for Goal5396 if native code is changed or full-trace parity is
attempted. Use only:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

Do not use naked SSH, and do not declare POD failure before wrapper preflight.

## Review Status

Current review-pending items:

```text
Goal5394 full-cover delta status probe
Goal5395 native status-stream ABI gate
```

Both are implemented with focused tests and call-for-review packets. They must
not be silently upgraded to externally reviewed until an external review exists.

## Allowed Summary

```text
X-HD has strong Level-B scalar correctness and real generic RTDL system
extraction. Goal5394 pinned the explicit -lb row-shape delta as a generic
full-cover-plus-delta probe, and Goal5395 turned that into an app-neutral native
status-stream ABI while proving current v6 is insufficient. Full paper
reproduction remains incomplete: exact paper inputs and explicit -lb row/hash
parity are unresolved, and the next hard step is a generic native status-stream
backend or fail-closed -lb decision.
```

## Forbidden Summaries

Do not say:

```text
X-HD full paper reproduction is complete.
RTDL supports explicit -lb.
Goal5394 proves author parity.
Goal5395 implements the native backend.
Current v6 native status probe is sufficient.
The 6x-active delta is understood.
The public Dragon -> HappyBuddha pair is the exact paper input.
RTDL has same-denominator performance parity with the author.
```
