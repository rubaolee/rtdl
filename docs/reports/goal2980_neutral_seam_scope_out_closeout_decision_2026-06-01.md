# Goal2980 Neutral-Seam Scope-Out Closeout Decision

Date: 2026-06-01

Status: C-3 decision encoded; v2.5 scopes out full partner-neutral composition

## Purpose

The Claude v2.5 closeout roadmap asked for a deliberate C-3 decision on the
neutral-buffer seam. It named two honest choices:

- fix the seam in v2.5 so every partner can use a genuinely partner-neutral
  DLPack / CUDA-array-interface path; or
- scope it out and state plainly that multi-partner composition is scaffolded,
  not delivered, in v2.5.

Goal2980 chooses the second option for v2.5. This is the faster and more honest
closeout because Goal2979 reinforces the primitive-first rule: the current v2.5
value is app-agnostic RTDL primitives plus explicit partner continuations where
needed, not a full multi-partner residency layer.

## Encoded Decision

The new machine-readable decision is:

- `v2_5_neutral_seam_closeout_decision()`
- `validate_v2_5_neutral_seam_closeout_decision()`

The decision records:

| Field | Value |
| --- | --- |
| selected option | `C-3b_scope_out_for_v2_5` |
| multi-partner composition scaffolded | `true` |
| multi-partner composition delivered | `false` |
| full partner-neutral handoff delivered | `false` |
| Torch carrier status | `bounded_triton_launch_carrier_not_neutral_seam` |
| Torch carrier allowed partners | `("triton",)` |
| non-Triton carrier route | `cuda_array_interface_descriptor` |
| true zero-copy authorized | `false` |
| automatic Triton selection allowed | `false` |
| v2.5 release authorized | `false` |

## Interpretation

This does not remove the existing Torch carrier path. It makes its status
explicit:

- Torch can still be used as a bounded Triton launch carrier for the existing
  Triton path.
- Torch is not a neutral protocol.
- Non-Triton partners must use explicit descriptor or partner-owned paths.
- The neutral seam remains the authority for transfer/copy/lifetime metadata.
- Full partner-neutral composition is deferred to v3.0 or later, where the
  residency-first plan can make it worth doing.

## Delivered vs Not Delivered

Delivered in v2.5:

- typed hit-stream and payload handoff scaffold;
- neutral-seam authority metadata and runtime trace;
- bounded Triton launch carrier for Triton-only paths;
- descriptor routes for non-Triton partners;
- primitive-first selection policy.

Not delivered in v2.5:

- end-to-end partner-neutral device-resident composition;
- true zero-copy contract;
- automatic Triton selection;
- partner-composition public speedup claim;
- v3.0 residency pipeline.

Deferred to v3.0 or later:

- native device-resident hit-stream output state machine;
- partner-neutral DLPack / CUDA-array-interface execution without the Torch
  carrier;
- CUDA-Graph or event-ordered resident pipeline;
- whole-app residency measurement on at least one app.

## Validation

Focused validation:

```text
PYTHONPATH=src;. py -3 -m py_compile src\rtdsl\hit_stream_handoff.py src\rtdsl\__init__.py src\rtdsl\v2_5_internal_readiness.py tests\goal2980_neutral_seam_scope_out_closeout_decision_test.py
PYTHONPATH=src;. py -3 -m unittest tests.goal2980_neutral_seam_scope_out_closeout_decision_test tests.goal2775_hit_stream_neutral_seam_reconciliation_test tests.goal2879_torch_carrier_seam_authority_provenance_test tests.goal2883_torch_carrier_runtime_seam_trace_test tests.goal2979_representative_same_contract_gate_after_primitive_first_policy_test tests.goal2806_v2_5_internal_readiness_packet_test
```

## Boundary

Goal2980 is a closeout decision, not a release authorization. It does not
authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper reproduction claims;
- app-specific native engine customization.

The next roadmap item is C-4: write the v2.5 closeout report and ask for
external review before any user-requested release packet.
