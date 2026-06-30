# Goal2740 - Hit-Stream Cross-Partner Transfer Plan

Date: 2026-05-30

Status: local Codex implementation complete; external review pending.

## Purpose

Goal2736-Goal2739 hardened the v2.5 direction around primitive-first RTDL
planning, native hit-stream owner lifetime, and CUDA producer/consumer stream
ordering. The next exposed gap was cross-partner transfer semantics: the current
typed hit-stream path had good neutral-buffer metadata, but the executable
gather helper still made the planning surface feel Torch/Triton-centered.

Goal2740 adds an explicit per-partner transfer plan for RTDL hit streams and
typed primitive payload columns. The plan tells the app exactly what carrier is
selected for each partner, whether the row is executable, descriptor-only, or
fail-closed, and whether any copy or host materialization is required.

## Design

The new function is:

```python
rt.plan_v2_5_hit_stream_partner_transfer(
    hit_stream_columns,
    payload_columns,
    operation="segmented_sum_f64",
    partner="triton",
)
```

It returns a plan/explain record with these key fields:

- `status`: one of `host_reference_ready`,
  `explicit_host_materialization_required`, `torch_carrier_preview`,
  `cuda_descriptor_preview`, `descriptor_only`, or `unsupported_fail_closed`.
- `carrier_protocol`: one of `host_columns`, `torch_tensor_carrier`,
  `cuda_array_interface_to_torch_carrier`, `cuda_array_interface_descriptor`,
  `neutral_buffer_descriptor`, or `none`.
- `silent_copy_forbidden`: always `True`.
- `execution_allowed_without_copy`: true only when the selected partner can use
  the current buffers without an implicit copy or host stage.
- `descriptor_only`: true for current CuPy conformance rows.
- `executable_preview_available`: true for preview rows that still require
  explicit runtime/hardware validation.
- `stream_synchronization_proven`: propagated from the hit-stream handoff.
- `true_zero_copy_authorized` and `public_speedup_claim_authorized`: both remain
  `False`.

The existing `plan_v2_5_hit_stream_partner_continuation(...)` now nests this
record as `partner_transfer_plan` while preserving its previous top-level
compatibility fields.

## Partner Semantics

| Partner | Current v2.5 transfer meaning |
| --- | --- |
| Python reference | Host columns are ready; CUDA/device columns require explicit host materialization. |
| Triton | Device-ready columns select the Torch tensor / CUDA-array-interface-to-Torch carrier preview; pod evidence is still required before claims. |
| CuPy | Device-ready columns are descriptor-only conformance/interoperability metadata in this generic hit-stream slice; no generic CuPy kernel execution is implied. |
| Numba | Supported narrow operations get a CUDA descriptor preview; unsupported operations fail closed. |

This keeps the RTDL engine app-agnostic and partner-neutral. Triton remains the
primary preview partner, CuPy remains conformance/interoperability, and Numba
remains a narrow fallback preview. None of them is allowed to replace RTDL/OptiX
RT traversal.

## Files Changed

- `src/rtdsl/hit_stream_handoff.py`
  - Added `GENERIC_HIT_STREAM_PARTNER_TRANSFER_PLAN_VERSION`.
  - Added transfer status and carrier protocol vocabularies.
  - Added `plan_v2_5_hit_stream_partner_transfer(...)`.
  - Nested the transfer plan in `plan_v2_5_hit_stream_partner_continuation(...)`.
  - Hardened explicit Triton gather so raw CUDA-array-interface columns require
    either an existing Torch tensor carrier or hardware-proven native CUDA
    columns before runtime adaptation is attempted.
- `src/rtdsl/__init__.py`
  - Imported the experimental planning symbols without adding them to
    `rt.__all__`.
- `tests/goal2740_hit_stream_cross_partner_transfer_plan_test.py`
  - Added regression coverage for Python reference, Triton, CuPy, Numba,
    unsupported fail-closed behavior, and non-star-export status.

## Validation

Local Windows validation:

```text
py -3 -m unittest tests.goal2740_hit_stream_cross_partner_transfer_plan_test
7 tests OK

py -3 -m unittest \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2737_native_hit_stream_owner_lifecycle_guard_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test \
  tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test \
  tests.goal2734_v2_5_same_pointer_zero_copy_boundary_audit_test
45 tests OK

py -3 -m py_compile src/rtdsl/hit_stream_handoff.py src/rtdsl/__init__.py \
  tests/goal2740_hit_stream_cross_partner_transfer_plan_test.py
clean
```

Pod validation on `root@69.30.85.171:22167` after pulling commit `613f250e`:

```text
python3 -m unittest \
  tests.goal2740_hit_stream_cross_partner_transfer_plan_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2738_native_hit_stream_stream_ordering_boundary_test \
  tests.goal2737_native_hit_stream_owner_lifecycle_guard_test \
  tests.goal2704_native_hit_stream_output_abi_contract_test \
  tests.goal2708_hit_stream_cuda_array_torch_carrier_adapter_test
41 tests OK
```

## Boundary

This is a contract/planning hardening goal, not a new performance result.

- No native ABI was changed.
- No new true-zero-copy claim is authorized.
- No public speedup claim is authorized.
- CuPy remains descriptor-only for the current generic hit-stream continuation
  slice.
- Triton and Numba execution remain preview-gated by their existing runtime and
  hardware validation boundaries.

## Next Review Ask

Ask Claude or Gemini to review whether Goal2740 closes the cross-partner
transfer ambiguity raised after Goal2734-Goal2739 without accidentally
promoting a partner, authorizing silent copies, or weakening the v2.5 public
claim boundary.
