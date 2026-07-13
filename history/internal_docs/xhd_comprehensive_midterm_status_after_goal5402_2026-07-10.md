# X-HD Comprehensive Midterm Status After Goal5402

Date: 2026-07-10

Status label:

```text
level_b_scalar_strong__generic_system_extraction_real__generic_status_state_native_smoke_passed__bounded_app_oracle_pending__full_paper_not_complete
```

## Executive Summary

X-HD full paper reproduction is still not complete. The scalar Level-B
Dragon -> HappyBuddha route remains strong, generic RTDL system extraction is
real, and Goal5402 now closes the first native synthetic smoke for the
Goal5401 generic status-state-machine contract.

What changed since the previous local-only snapshot:

```text
Goal5402 now has POD focused tests, POD native build, POD native smoke artifact,
and result/call-for-review documents.
```

What did not change:

```text
explicit X-HD -lb remains unsupported;
Goal5387 author trace row/hash parity remains unproved;
Figure 7/11 remain unreproduced;
exact paper datasets remain unavailable;
full X-HD paper reproduction remains open.
```

## Current Strong Evidence

### Bounded And Generic Extraction

Reviewed/completed:

```text
Goal5110 scaffold/provenance;
Goals5111-5126 bounded same-input value reproduction and directed contract;
Goals5127-5128 generic nearest/witness/max-nearest extraction plus non-HD consumer;
Goal5129 full-reproduction plan with exact-dataset provenance discipline.
```

### Level-B Public Scalar Correctness

Strongest current representative line:

```text
source = public Stanford Dragon
target = public Stanford HappyBuddha
source points = 437,645
target points = 543,652
author hd_exec HDResult = 0.12572988867759705
RTDL route distance = 0.12572988629271128
abs diff ~= 2.38e-9
```

This is Level-B same-source public evidence, not exact paper dataset
reproduction.

### Route Performance, With Caveat

Current route-local fast scalar line:

```text
Goal5211 fresh route ~= 0.849s
Goal5212 fresh total including load ~= 1.531s
Goal5211 explicit-warm route median ~= 0.362s
Goal5212 explicit-warm measured case total ~= 0.288s
```

Caveat:

```text
per_source_witness_exact = false
409,376 / 437,645 sources early-abort
```

This route preserves the directed-HD scalar value but may leave early-aborted
per-source witnesses approximate. It is valid only under the max-nearest /
directed-HD scalar contract.

## Current Hard Blocker: Explicit `-lb`

Author oracle from Goal5387:

```text
active queries = 437,645
raw offload rows = 27,133,990
raw hash = 4333109858711462591
feedback_update_count = 294
```

RTDL native v7 parity gate from Goal5398:

```text
active_query_count_parity = true
RTDL v7 rows = 2,600,727
row_count_parity = false
hash_parity = false
```

Goal5400 existing knob matrix:

```text
active-initial/default surfaces under-count badly;
emit-pruned/heavy-before-inline surfaces overflow by orders of magnitude;
existing knobs are exhausted.
```

Decision:

```text
continue only through a generic active-query status-state machine spike;
stop if parity requires X-HD-specific constants or author-only semantics.
```

## Goal5401 / Goal5402 Status

Goal5401 contract:

```text
ACTIVE_QUERY_STATUS_STATE_MACHINE_NATIVE_SPIKE_CONTRACT
raw_offload_before_continuation_reduce
post_continuation_feedback
row/hash/status/feedback gates
fail-closed overflow/mismatch behavior
```

Goal5402 implementation:

```text
rtdl_optix_active_query_status_state_machine_smoke_v1
active_query_status_state_machine_smoke_native(...)
```

Goal5402 POD artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5402_status_state_machine_native_smoke_pod.json
```

POD smoke result:

```text
matched = true
status = native_status_state_machine_smoke_passed
valid_count = 2
attempted_count = 2
raw_offload_row_count = 2
status_count_offloading = 2
feedback_update_count = 1
native_generic_symbol = rtdl_optix_active_query_status_state_machine_smoke_v1
contract = generic_active_query_status_state_machine_native_spike_v1
```

Validation:

```text
local focused tests = Ran 23 OK
POD preflight = POD_OK on NVIDIA RTX 4000 Ada Generation
POD focused tests before smoke = Ran 13 OK
POD make build-optix = succeeded
POD native smoke = matched true
POD focused tests after artifact sync = Ran 10 OK
```

Goal5402 documents:

```text
history/internal_docs/goal5402_generic_status_state_machine_native_smoke_result_2026-07-10.md
history/internal_docs/call_for_review_goal5402_generic_status_state_machine_native_smoke_2026-07-10.md
```

## Claim Boundary

Allowed:

```text
Goal5402 proves a synthetic generic native status-state smoke.
```

Not allowed:

```text
explicit X-HD -lb support;
Goal5387 row-count parity;
Goal5387 hash/sample parity;
Figure 7 reproduction;
Figure 11 reproduction;
performance parity;
exact paper dataset reproduction;
full X-HD paper reproduction.
```

## Completed Problems

1. Direction semantics are locked as directed input1 -> input2, not symmetric.
2. Exact pairwise materialization was avoided for full public Dragon/HappyBuddha.
3. Generic nearest/witness/max-nearest and cell-MBR frontier APIs were extracted.
4. Route-local scalar performance improved dramatically while preserving scalar
   HDResult.
5. Existing status-stream knobs were exhausted before writing more native code.
6. A generic status-state contract now exists.
7. A synthetic native status-state smoke now builds and executes on POD.

## Remaining Problems

1. Exact paper input file/hash provenance is still missing.
2. Explicit `-lb` author trace parity is still missing.
3. Figure 7/8/9/10/11 reproduction is still missing.
4. Author-vs-RTDL performance ratio is still unauthorized.
5. Many goals in the larger X-HD line remain implemented / review pending.

## Next Planned Work

Immediate next decision:

```text
Goal5403 should choose the next status-state oracle gate:

Option A: bounded X-HD app oracle gate using a small status-state fixture;
Option B: direct full Goal5387 oracle gate if native inputs are ready;
Option C: fail-close explicit -lb if the next gate requires X-HD-specific
          semantics in RTDL core/native.
```

A valid next gate must compare:

```text
active_count;
raw row_count;
raw row hash or deterministic sample;
status_count_offloading;
feedback_update_count or explicit generic not-applicable evidence;
overflow/fail-closed behavior.
```

POD expectation:

```text
Any native continuation of Goal5402 requires POD and scripts/current_pod_ssh.py.
Do not use naked SSH.
```

## Bottom Line

Goal5402 is real progress: it takes the Goal5401 generic contract from design
to a built native symbol that executes on POD. But it is still only a synthetic
smoke. The decisive question remains whether the same generic status-state
machinery can close the Goal5387 author trace row/hash/status/feedback gap
without smuggling X-HD-specific semantics into RTDL core.
