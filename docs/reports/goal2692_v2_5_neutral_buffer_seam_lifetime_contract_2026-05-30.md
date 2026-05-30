# Goal2692 V2.5 Neutral Buffer Seam And Lifetime Contract

Date: 2026-05-30
Status: local implementation and Windows contract validation complete; pod validation not required for this slice
Commit basis: after Goal2690

## Purpose

Goal2692 answers the main v2.5 design blocker identified across the fresh
Claude reviews and the partner-composition design report: RTDL needs a neutral
buffer seam before app authors can honestly choose Torch/Triton, CuPy,
Numba, raw CUDA, or CPU continuation per phase.

This goal is deliberately not the native OptiX CUDA-output implementation. It
is the contract layer that must exist first so later native columns, partner
continuations, and multi-partner apps do not silently privilege Torch, hide
copies, or overclaim zero-copy.

## What Changed

Added `src/rtdsl/neutral_buffer_seam.py` with:

| Surface | Purpose |
| --- | --- |
| `describe_v2_5_neutral_buffer_seam_contract()` | Machine-readable v2.5 contract: protocol priority, transfer states, ownership states, no-forced-partner rule, and claim boundaries. |
| `classify_neutral_buffer_protocol(obj)` | Chooses the most specific supported protocol: registered partner adapter first, then generic DLPack, then raw CUDA array interface, then host array interface. |
| `neutral_buffer_descriptor_from_object(...)` | Converts Torch/CuPy/NumPy/DLPack/CUDA-array-interface/host-array-interface objects into one neutral seam descriptor. |
| `neutral_buffer_descriptor_from_rtdl_buffer(...)` | Wraps an existing `RtdlBufferDescriptor` in the same seam contract. |
| `RtdlNeutralBufferSeamDescriptor` | Records producer, consumer, transfer/copy status, lifetime state, host-materialization state, measured zero-copy evidence, and claim flags. |
| `RtdlNeutralBufferLifetimePlan` | Defines the first fail-closed ownership/lifetime transition model for caller-retained, producer-retained, partner-borrowed, pending-native-owned, and released states. |
| `validate_neutral_buffer_lifetime_transition(...)` | Rejects invalid transitions such as using a released buffer again. |

The symbols are imported at `rtdsl` module scope for internal/experimental use
but are intentionally not added to `rtdsl.__all__`, matching the Goal2688
experimental-surface rule.

## Contract Rules

Protocol priority:

1. Registered partner adapter (`torch`, `cupy`, `numpy`) when the object is a
   known partner object and exportable.
2. Generic DLPack.
3. Raw `__cuda_array_interface__`.
4. Host `__array_interface__`.

This avoids the current v2.5 risk where a CUDA-capable object can be coerced
through a Torch-shaped branch even if the app author chose CuPy or another
partner.

Transfer status is explicit:

| Status | Meaning |
| --- | --- |
| `host_reference` | CPU/host reference buffer. |
| `declared_copy` | A copy is part of the plan. |
| `host_stage` | Host staging is part of the plan. |
| `borrowed_device_pointer_unmeasured` | A CUDA pointer is visible, but no zero-copy proof exists. |
| `zero_copy_measured` | Same pointer / same device / no host stage was measured. |
| `unknown` | The contract could not infer transfer status. |

Zero-copy authorization is intentionally narrow. A descriptor only reports
`zero_copy_claim_authorized=True` when all of these hold:

- transfer status is `zero_copy_measured`;
- a non-zero CUDA pointer is observed;
- same-pointer evidence is recorded;
- no-host-stage evidence is recorded;
- the handoff did not materialize host data first.

Even then, `public_speedup_claim_authorized=False` and
`native_device_output_promotion_ready=False`. This contract can represent
measured zero-copy evidence, but it does not by itself prove performance or
native RTDL output.

## Ownership And Lifetime

Goal2692 adds a small fail-closed lifetime model:

| State | Meaning |
| --- | --- |
| `caller_retained` | Caller owns and must keep the buffer alive. |
| `producer_retained` | Producer owns and retains until continuation completes. |
| `partner_borrowed` | Consumer temporarily borrows the buffer. |
| `native_owned_pending_state_machine` | Future native owner exists, but exact allocation/release state machine is not yet implemented. |
| `released` | Buffer must not be reused. |

Allowed transitions are explicit, for example:

- `producer_retained -> partner_borrowed` via `handoff_begin`;
- `partner_borrowed -> producer_retained` via `continuation_complete`;
- `partner_borrowed -> released` via `failure_cleanup`;
- `released -> partner_borrowed` is rejected.

This is still a contract-level state machine. The native CUDA allocator,
overflow cleanup, and failure cleanup implementation remain future work.

## Review Issue Coverage

| Prior issue | Goal2692 response |
| --- | --- |
| Torch coercion narrows app partner choice | Adds neutral protocol classification and descriptors that do not privilege Torch. |
| Multi-partner composition lacks a boundary object | Adds one seam descriptor that can name any producer/consumer pair. |
| Copy/zero-copy status can be ambiguous | Adds explicit `transfer_status`, `copy_status`, and measured-evidence flags. |
| Lifetime is only prose/metadata | Adds a first fail-closed lifetime transition model. |
| Native CUDA output could be promoted too early | Keeps `native_device_output_promotion_ready=False` and does not put symbols in `__all__`. |
| Public speedup / zero-copy overclaim risk | Keeps public speedup false and requires measured same-pointer/no-host-stage evidence for zero-copy authorization. |

## Validation

Windows:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2692_neutral_buffer_seam_lifetime_contract_test
Ran 7 tests in 0.003s
OK
```

Windows focused v2.5 contract suite:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 64 tests in 7.896s
OK (skipped=5)
```

Local Linux validation on `192.168.1.20`, fresh checkout
`/home/lestat/work/rtdl_goal2692_linux_check`, commit
`b6653721fdf440258ec19a4a357d6af5b51c3c08`:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 64 tests in 11.747s
OK (skipped=5)

python3 -m py_compile src/rtdsl/neutral_buffer_seam.py src/rtdsl/__init__.py \
  tests/goal2692_neutral_buffer_seam_lifetime_contract_test.py
OK
```

The test covers:

- contract shape and claim boundaries;
- registered partner adapter priority over generic protocols;
- generic DLPack priority over raw CUDA array interface;
- raw CUDA array interface fallback;
- host array interface reference mode;
- zero-copy evidence fail-closed behavior;
- lifetime transitions and invalid-transition rejection;
- experimental symbols are importable but absent from `rtdsl.__all__`.

## Boundary

Goal2692 does not:

- create native OptiX CUDA-resident hit-stream output;
- remove the current host-row bridge in the hit-stream implementation;
- prove true zero-copy on hardware;
- prove speedup;
- make Triton mandatory;
- make RTDL a general-purpose memory manager;
- authorize public v2.5 release claims.

## Next Work

1. Rewire the hit-stream and typed-payload handoff internals to produce and
   consume `RtdlNeutralBufferSeamDescriptor` metadata so Torch, CuPy, and raw
   CUDA paths share one boundary.
2. Add a supported `(partner x operation x backend)` matrix that references the
   neutral seam.
3. On an `sm_70+` pod, measure same-pointer/no-host-stage evidence for the
   first true native OptiX CUDA output path before setting any zero-copy flag.
4. Get an external review for Goal2692 before using it as a prerequisite for
   the native device-column implementation.
