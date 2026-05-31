# Goal2789 - Neutral Buffer / Triton Tensor-Carrier Reconciliation

Date: 2026-05-31

## Purpose

Goal2773's external review flagged a real architecture risk: v2.5 already has a
neutral-buffer seam, but the hit-stream handoff still had an old helper named
`_maybe_torch_column`. That name made the Triton tensor-carrier path look like
an implicit torch coercion seam rather than an explicitly bounded partner
carrier.

Goal2789 reconciles that boundary without pretending Triton no longer uses
Torch tensors as its Python launch carrier.

## What Changed

Updated:

- `src/rtdsl/hit_stream_handoff.py`

Added:

- `tests/goal2789_neutral_buffer_torch_carrier_reconciliation_test.py`

The old helper name is gone:

```text
_maybe_torch_column -> _prepare_triton_tensor_carrier_column
```

This is a naming and boundary hardening step. It keeps the existing behavior
but makes the design intent explicit:

- Triton may use a torch tensor carrier for launch compatibility.
- That carrier is allowed only for the Triton partner path.
- It is accounted for by neutral-buffer seam metadata.
- It is not true zero-copy.
- Silent cross-partner torch coercion remains disallowed.

## Boundary

This goal authorizes:

- explicit Triton tensor-carrier preparation terminology;
- tests that prevent the old implicit helper name from returning;
- continued neutral-buffer accounting for host-stage and device-resident
  handoffs.

This goal does not authorize:

- true zero-copy claims;
- public speedup claims;
- RT-core speedup claims;
- v2.5 release readiness;
- treating torch as the generic partner seam for non-Triton partners.

## Validation

Local Windows validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2703_neutral_buffer_lease_state_machine_test \
  tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test

Ran 39 tests in 0.393s
OK (skipped=1)

py_compile with PYTHONPYCACHEPREFIX=scratch\pycache_goal2789_local
OK
```

Pod validation:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2789_neutral_buffer_torch_carrier_reconciliation_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2703_neutral_buffer_lease_state_machine_test \
  tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test

Ran 39 tests in 1.534s
OK (skipped=1)
```

## Decision

`accept-with-boundary`

Goal2789 is accepted as a seam-clarity and regression-guard step. It does not
make the handoff zero-copy or release-ready; it removes the misleading implicit
coercion surface and keeps the Triton carrier path bounded by neutral-buffer
metadata.
