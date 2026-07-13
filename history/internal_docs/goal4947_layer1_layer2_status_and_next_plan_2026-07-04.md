# Goal4947 - Layer 1/2 Status And Next Plan

## Status

`planning_ready__after_goal4946_native_device_columns_to_numba_execution`

This document records the current state after Goals 4942 through 4946 and defines the next work sequence. It is a status and planning packet, not a release claim and not a performance claim.

## Executive Summary

The project has now completed the first real Layer 1/2 execution chain:

```text
RTDL native primitive producer
  -> generic device-column row-buffer
  -> v2.6 neutral Numba handoff
  -> generic Numba numeric continuation execution
```

The important change is that the work moved from "handoff planning" to real CUDA execution over a native RTDL primitive-produced device column.

The proven hardware chain is:

```text
directed point-location/PIP native face_id device column
  -> RtdlDeviceColumnRowBuffer
  -> Numba CUDA uint32_equal_mask
```

The observed result on the POD was:

```json
{
  "row_count": 3,
  "ids_device_ptr_observed": true,
  "handoff_status": "accept",
  "numba_operation": "uint32_equal_mask",
  "mask_values": [true, true, false],
  "mask_true_count": 2,
  "host_column_materialization_used": false,
  "app_specific_semantics_allowed": false
}
```

This is a real capability milestone. It is not yet a RayJoin performance milestone.

## Current Git State

Latest relevant commits:

```text
b963d82ed Complete Goal4946 native device columns to Numba
c92c3f4ea Document Goal4945 native PIP runtime gate
277a4e0c7 Add Goal4945 native PIP carrier runtime gate plan
69442cf77 Complete Goal4944 local PIP device column carrier
ebcd77a63 Complete Goal4943 LSI PIP producer audit
5d8903dd5 Complete Goal4942 device column row buffer handoff
```

The working tree was clean when this packet was created.

## What Has Been Completed

### Goal4942 - Device-Column Row-Buffer Handoff

Goal4942 defined the generic Layer 1 carrier:

```text
RtdlDeviceColumnRowBuffer
```

This row-buffer reuses the existing v2.5/v2.6 device-column and neutral partner handoff work instead of inventing a new memory system.

Key properties:

- accepts named primitive-output columns;
- records source mode, row count, producer, phase timing, and stream-ordering status;
- delegates partner validation to the v2.6 neutral handoff path;
- keeps app-specific schemas out of RTDL core;
- does not authorize true-zero-copy wording, speedup wording, or release wording.

The important design rule is:

```text
row-buffer is a carrier, not a new application model
```

### Goal4943 - LSI/PIP Producer Audit

Goal4943 audited whether existing LSI and PIP producers could feed the Layer 1 row-buffer.

Findings:

- LSI already had Python-visible native pair-id device columns in the relevant path.
- PIP/direct point-location had native device execution, but Python could observe only row counts.
- PIP lacked a safe device-column pointer carrier for `face_id` and `segment_id`.

This identified the exact gap that Goal4944 needed to close.

### Goal4944 - PIP Directed Point-Location Device-Column Carrier

Goal4944 added native and Python carrier support for PIP/direct point-location id columns.

New generic native output record:

```cpp
struct RtdlNativePointLocationDeviceIdColumns {
    uint64_t ids_device_ptr;
    uint64_t row_count;
    uint64_t capacity;
    uint32_t overflow;
    int32_t device_ordinal;
    double traversal_seconds;
};
```

New directed point-location ABI symbols:

```text
rtdl_optix_prepared_directed_segment_point_location_2d_device_segment_id_columns
rtdl_optix_prepared_directed_segment_point_location_2d_device_face_id_columns
```

Key ownership repair:

- before: `face_id` used a temporary native `DevPtr` and could not safely expose a pointer after return;
- after: prepared query-points state owns `d_face_ids`, matching the persistent `d_segment_ids` pattern.

Python carrier:

```python
PreparedOptixRayjoinCdbPointLocation2D.segment_id_device_columns(...)
PreparedOptixRayjoinCdbPointLocation2D.face_id_device_columns(...)
```

Layer 1 adapter:

```python
device_column_row_buffer_from_point_location_id_columns(...)
```

This adapter accepts only:

```text
face_id
segment_id
```

It deliberately rejects app-specific names such as output-chain or overlay schema names.

### Goal4945 - Native POD Runtime Gate

Goal4945 proved the Goal4944 native path on NVIDIA hardware.

POD:

```text
host: 157.157.221.29:24344
key: ~/.ssh/id_ed25519_rtdl_codex_current_pod
container: ce489c3fad22
project path: /root/rtdl_goal4937
```

Build:

```bash
cd /root/rtdl_goal4937
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev CUDA_PREFIX=/usr/local/cuda-12.8
```

Result:

```text
build-optix: pass
```

Runtime fixture proved:

- `segment_id_device_columns(...)` returns native device-column metadata;
- `face_id_device_columns(...)` returns native device-column metadata;
- both columns report nonzero device pointers;
- both columns adapt into the Layer 1 row-buffer;
- both are accepted by the v2.6 Numba handoff planner.

Antigravity verdict:

```text
approve_goal4945_native_pip_device_column_runtime_gate
```

This closed the native hardware gate for PIP id columns.

### Goal4946 - Native Device Columns To Numba Execution

Goal4946 moved beyond handoff planning into real Numba CUDA execution.

It added one small generic Layer 2 continuation:

```text
uint32_equal_mask
```

Contract:

```text
input column: values:uint32
scalar input: target:uint32
output:       mask:bool
behavior:     mask[i] = values[i] == target
```

This is not RayJoin logic. It is a generic id-column filter.

Local verification:

```text
Ran 14 tests in 0.029s
OK (skipped=4)
```

POD verification:

```text
Ran 10 tests in 0.854s
OK
```

Final runtime chain:

```python
face_cols = prepared.face_id_device_columns(prepared_points)
face_rb = rt.device_column_row_buffer_from_point_location_id_columns(face_cols)
handoff = rt.prepare_device_column_row_buffer_partner_handoff(face_rb, partner="numba")
mask = rt.run_numba_uint32_equal_mask(face_rb.columns["face_id"], target=100)
```

Observed:

```json
{
  "mask_values": [true, true, false],
  "mask_true_count": 2,
  "host_column_materialization_used": false,
  "app_specific_semantics_allowed": false
}
```

Antigravity initial verdict:

```text
approve_goal4946_native_device_columns_to_numba_execution
```

Antigravity also identified a real completeness gap: `execute_v2_5_partner_continuation_reference(...)` lacked a Python reference fallback for `uint32_equal_mask`.

That gap was fixed in the same goal:

- Python reference branch added.
- `values` and `target` validate as `uint32`.
- focused tests added.

Antigravity amendment verdict:

```text
approve_goal4946_reference_fallback_amendment
```

## What Has Been Proven

The following statements are now supported by code, tests, POD evidence, and review:

1. RTDL can expose PIP/direct point-location `segment_id` and `face_id` as native device columns.
2. Those columns can be wrapped by the generic Layer 1 row-buffer.
3. The row-buffer can pass v2.6 neutral Numba handoff planning.
4. A generic Numba CUDA continuation can execute over a native RTDL primitive-produced device column.
5. The operation can remain app-neutral.
6. The path does not need a new partner API.

## What Has Not Been Proven

The following are explicitly not proven:

- RayJoin whole-app speedup.
- PIP application speedup.
- LSI application speedup.
- Layer 3 writer speedup.
- true-zero-copy public wording.
- release readiness.
- broad Numba partner superiority.
- full device-resident end-to-end RayJoin hot path.

The test fixture copies the final mask to host for correctness validation. That validation copy is not a public hot-path claim.

## Claude Review Intake

Claude reviewed this packet in:

```text
history/internal_docs/claude_review_goal4947_layer1_2_status_2026-07-04.md
```

Verdict:

```text
approve_goal4947_status_and_next_plan
```

The review approves proceeding with Goal4947 and adds three strategic amendments. These amendments are accepted and become part of this plan.

### Amendment 1 - Goal4949 Must Use Real RayJoin Hot-Path Continuations

The review correctly warns that `uint32_equal_mask` and candidate LSI demo continuations are generic but not RayJoin's real hot-path work.

Therefore Goal4949 must not remeasure RayJoin using demo operators. It must use RayJoin's actual numeric continuation phases:

- reprojection;
- sort/order work;
- dedupe;
- midpoint candidate generation;
- any other measured numeric continuation that appears in the RayJoin hot path.

If Goal4949 uses unrelated demo operators and finds no phase movement, that result is not meaningful. It would only prove that the wrong work was measured.

### Amendment 2 - Keep Layer 3 Writer As The Larger Prize

The review also correctly notes that Layer 1/2 attacks only part of the hot path.

Approximate current budget:

```text
Layer 2 numeric continuation target: ~0.8-0.9 s
Layer 3 writer / output assembly:    ~1.7-1.9 s
```

So Goal4949 and Goal4951 must not over-invest in Layer 2 just because the plumbing is now working. If the remeasure shows Layer 2 has small remaining upside, the correct decision is to move to Layer 3.

### Amendment 3 - Goal4948 Must Show Useful Non-RayJoin Work

The genericity gate must not be another wiring-only proof.

Goal4948 must show the row-buffer plus Numba continuation machinery doing useful work for a structurally different non-RayJoin workload. A mere "foreign column enters the buffer" test is not sufficient.

Acceptable direction:

```text
non-RayJoin native device columns
  -> row-buffer
  -> generic numeric Numba continuation
  -> checked useful result
```

Examples include kNN plus reduction, hit-stream grouped reduction, or another non-RayJoin spatial/RT primitive with a real downstream numeric task.

### Layer 3 Drift Check

Claude asked whether `src/rtdsl/output_assembly.py` represents quiet Layer 3 drift.

Checked status:

```text
src/rtdsl/output_assembly.py is pre-existing work from:
- 36754ae54 Add generic output assembly smoke evidence
- ce8271ecf Complete Goal4935 output row buffer contract
- a40f1a419 Complete Goal4936 generic output materializer
- d9c7d0b1f Complete Goal4939 grouped path split prototype
```

It is not a new change in Goals 4942-4947 and was not modified by this Layer 1/2 status packet.

Conclusion:

```text
no new Layer 3 drift detected in this packet
```

## Why This Matters

The previous performance diagnosis said that RTDL was slow partly because Python sat between stages. Layer 1/2 attacks a specific part of that problem:

```text
native RTDL primitive output should remain in device-column form
and be consumed by partner continuations without Python row materialization
```

Goal4946 proves that this is not just an idea. The first hardware path works.

The result is still a capability gate, not a performance gate.

## Relation To The Layer 0/1/2/3 Plan

### Layer 0

Layer 0 decomposed the RayJoin hot path and found that output/writer work and residual numeric continuation work should be treated separately.

Layer 0 also warned against making implementation claims before phase evidence.

### Layer 1

Layer 1 is the device-column row-buffer foundation. Goals 4942 through 4945 substantially complete the first proof:

```text
native producer -> generic row-buffer -> neutral partner handoff
```

PIP now has a native hardware-proven carrier.

### Layer 2

Layer 2 is device numeric continuation. Goal4941 had already created generic Numba operations over caller-supplied device arrays.

Goal4946 proves the missing bridge:

```text
native producer output -> Layer 2 Numba execution
```

This is the first executable proof of the Layer 1/2 combination.

### Layer 3

Layer 3 is compiled output/structure assembly. Nothing in Goals 4942 through 4946 solves the writer bottleneck.

Layer 3 remains separate and should not be quietly restarted until the post-Layer1/2 phase table shows it is the right target.

## Next Work Plan

### Goal4947 - LSI Pair Columns To Numba Execution

Purpose:

Prove the same producer-to-Layer-2 execution chain for LSI native pair columns.

Expected path:

```text
LSI native left_id/right_id device columns
  -> device_column_row_buffer_from_native_pair_columns(...)
  -> generic Numba continuation
```

Candidate continuation:

```text
segmented_count_i64
```

or another already-existing generic continuation that consumes id columns without app semantics.

Boundary:

This goal is still a capability/execution proof. It must not be treated as RayJoin performance progress unless the selected continuation corresponds to a measured RayJoin phase.

Exit gate:

- LSI native device columns enter row-buffer.
- Numba CUDA continuation executes.
- correctness is checked on a small controlled fixture.
- no RayJoin app speedup claim.

### Goal4948 - Non-RayJoin Genericity Gate

Purpose:

Prove that the Layer 1/2 path is not merely a RayJoin-shaped solution.

Work:

Find one non-RayJoin workload that has native device-column output and connect it to an existing generic Numba continuation through the same row-buffer path.

Exit gate:

- non-RayJoin primitive-produced device columns enter row-buffer;
- Numba continuation executes;
- the continuation performs useful work for that non-RayJoin workload;
- correctness is checked against a small oracle;
- genericity claim becomes stronger than "RayJoin only."

### Goal4949 - RayJoin Hot-Path Phase Remeasure

Purpose:

After Goal4945/4946, remeasure the RayJoin hot path and decide whether Layer 2 is worth extending.

Questions:

- Does PIP id filtering or LSI grouping move a meaningful phase?
- Is the remaining cost still dominated by writer/structure assembly?
- Does Layer 2 have a measurable target, or should we stop and move to Layer 3?

Required measurement discipline:

- use real RayJoin numeric continuation phases, not demo operators;
- include reprojection, sort/order, dedupe, and midpoint work if present in the hot path;
- report Layer 2 recoverable time separately from Layer 3 writer/output assembly time;
- explicitly compare the remaining Layer 2 opportunity against the larger Layer 3 opportunity.

Exit gate:

- phase table with before/after numbers;
- no broad speedup wording;
- explicit decision: continue Layer 2, stop Layer 2, or move to Layer 3.

### Goal4950 - Bounded RayJoin App Integration Only If Measured

Purpose:

If Goal4949 shows a real target, integrate the generic Layer 2 continuation into the rayjoin-paper app path.

Constraint:

Do not put RayJoin output-chain semantics into RTDL core.

Exit gate:

- same correctness as current rayjoin-paper route;
- bounded phase improvement if present;
- no whole-app claim unless same-contract end-to-end measurement supports it.

### Goal4951 - Review And Direction Decision

Purpose:

Use evidence from Goals 4947 through 4950 to decide the next branch:

1. continue Layer 2 expansion;
2. stop Layer 2 and move to Layer 3 writer/structure assembly;
3. stop performance work and keep the result as capability infrastructure.

Decision rule:

Do not continue Layer 2 merely because more generic continuations can be built. Continue Layer 2 only if Goal4949 shows that real RayJoin hot-path numeric continuation time is still large enough to justify the work. Otherwise, move to Layer 3 or stop.

Exit gate:

- external review;
- no silent goal drift;
- explicit next branch.

## Current Recommendation

Proceed with Goal4947 next.

Reason:

Goal4946 proved the PIP side. The next most direct and valuable check is whether LSI native pair columns can also enter real Numba execution through the same generic row-buffer path. That tells us whether the Layer 1/2 bridge covers both major RayJoin primitives or only PIP.

Do not start Layer 3 writer work yet.

Do not claim RayJoin acceleration yet.

Do not add RayJoin-specific continuation semantics to RTDL core.

## Summary In One Sentence

Goals 4942 through 4946 have proven the first executable Layer 1/2 bridge from native RTDL device columns into generic Numba CUDA continuation; the next step is to prove the same bridge for LSI, then validate genericity on a non-RayJoin workload, and only then remeasure RayJoin to decide whether Layer 2 should continue or the work should move to Layer 3.
