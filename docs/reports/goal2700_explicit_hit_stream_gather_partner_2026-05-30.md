# Goal2700 Explicit Hit-Stream Gather Partner

Date: 2026-05-30
Status: local implementation; validation in progress
Depends on: Goal2692, Goal2694, Goal2696, Goal2698

## Purpose

Goal2700 reduces the Torch-coercion risk identified in the v2.5 reviews. The
existing `gather_typed_payload_columns_for_hit_stream(...)` API kept a
compatible `auto` behavior, but it did not let callers demand an explicit
partner boundary. This goal adds that boundary without changing the legacy
default.

## What Changed

`gather_typed_payload_columns_for_hit_stream(...)` now accepts:

```python
partner: str = "auto"
allow_explicit_copy: bool = False
```

Supported gather partner choices:

| Partner | Behavior |
| --- | --- |
| `auto` | Backward-compatible behavior: use Torch carrier if Torch tensors are already present, otherwise Python reference columns. |
| `python_reference` / `reference` | Force host/reference gather explicitly. |
| `triton` / `torch` | Requires existing Torch tensor carrier columns unless `allow_explicit_copy=True`; otherwise fails closed. |
| `cupy` / `cupy_conformance` | Descriptor/planning-only in this slice; execution fails closed. |
| `numba` | Descriptor/planning-only in this slice; execution fails closed. |

Returned metadata now includes:

- `requested_gather_partner`;
- `selected_gather_partner`;
- `explicit_partner_choice`;
- `allow_explicit_copy`.

This makes hidden copies harder to introduce accidentally. A Triton gather over
non-Torch columns must either fail closed or carry an explicit copy
authorization flag.

## Validation

Added `tests/goal2700_explicit_hit_stream_gather_partner_test.py`.

Initial Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test
Ran 45 tests in 0.900s
OK (skipped=1)
```

Windows focused v2.5 contract validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 82 tests in 7.758s
OK (skipped=5)

py -3 -m py_compile src\rtdsl\hit_stream_handoff.py \
  tests\goal2700_explicit_hit_stream_gather_partner_test.py
OK
```

The test covers:

- default `auto` remains compatible;
- `python_reference` can be requested explicitly;
- Triton gather fails closed without Torch carrier or explicit copy permission;
- CuPy and Numba descriptor-only choices do not execute gather;
- unknown gather partners fail closed.

## Boundary

Goal2700 does not:

- implement CuPy gather;
- implement Numba gather;
- remove the legacy `auto` behavior;
- prove Torch/Triton hardware execution;
- authorize public zero-copy or performance claims.

## Next Work

1. Run the expanded focused v2.5 suite on Windows and Linux.
2. Decide whether future v2.5 app paths should require explicit
   `partner=...` rather than legacy `auto`.
3. On pod, validate the Torch/Triton carrier path only after native device
   output exists or an explicit copy path is intentionally selected.
