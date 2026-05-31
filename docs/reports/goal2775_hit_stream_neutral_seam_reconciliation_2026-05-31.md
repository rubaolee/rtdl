# Goal2775 - Hit-Stream Neutral-Seam Reconciliation

Date: 2026-05-31

## Purpose

Goal2775 responds to the Goal2773 Claude finding that the v2.5 codebase had two
coexisting handoff stories:

- a real neutral-buffer seam in `neutral_buffer_seam.py`
- an older Torch-shaped carrier path in `hit_stream_handoff.py`

The fix is not to ban Torch. Triton needs Torch tensors as a practical launch
carrier in the current preview stack. The fix is to make the boundary explicit:
the neutral buffer seam is the authority for transfer, copy, ownership, and
claim metadata; Torch remains only a Triton launch carrier and never the neutral
protocol.

## What Changed

Added a reconciliation contract:

`describe_v2_5_hit_stream_neutral_seam_reconciliation()`

It records:

- neutral buffer seam is the authority
- support matrix is the authority for partner support
- Torch is not the neutral protocol
- Torch is not a v2.5 partner
- Torch carrier protocols are allowed only for Triton
- CuPy and Numba device paths use CUDA-array-interface descriptor carriers
- silent cross-partner Torch coercion is forbidden

The existing Torch adapter metadata now carries:

- `neutral_seam_reconciliation_version`
- `neutral_buffer_seam_contract_version`
- `support_matrix_is_authority=True`
- `torch_is_neutral_protocol=False`
- `torch_carrier_allowed_only_for_partner="triton"`
- `silent_cross_partner_torch_coercion_allowed=False`

The hit-stream transfer and continuation plans now also carry the reconciliation
version and explicit Torch-carrier flags. For non-Triton partners such as
`cupy_conformance` and `numba`, the carrier protocol remains
`cuda_array_interface_descriptor`, not a Torch carrier.

## Boundary

Goal2775 does not authorize:

- no public speedup claims
- no true zero-copy claims
- no release readiness
- no partner replacement of RTDL/OptiX traversal
- no claim that Torch is a required v2.5 partner

It is a contract hardening and audit goal. It does not add new kernels or pod
performance evidence.

## Files Changed

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `tests/goal2775_hit_stream_neutral_seam_reconciliation_test.py`

## Validation Plan

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test \
  tests.goal2775_hit_stream_neutral_seam_reconciliation_test
```

No pod is required for this goal because it is metadata/contract hardening. Pod
evidence remains required before any future public zero-copy or speedup claim.
