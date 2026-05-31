# Goal2741: Claude Review Of Goal2740 Cross-Partner Hit-Stream Transfer Plan

Date: 2026-05-30
Reviewer: Claude Sonnet 4.6
Verdict: `accept-with-boundary`

## Independence Statement

This is a read-only review based on direct inspection of source, tests, and
reports. No source code was modified.

## Scope

Files inspected:

- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `tests/goal2740_hit_stream_cross_partner_transfer_plan_test.py`
- `docs/reports/goal2740_hit_stream_cross_partner_transfer_plan_2026-05-30.md`
- `docs/reviews/goal2739_gemini_review_goal2736_2738_v25_primitive_lifetime_stream_2026-05-30.md`
- `src/rtdsl/v2_5_partner_support_matrix.py` (supporting context)

## Review Questions And Answers

### 1. Does `plan_v2_5_hit_stream_partner_transfer(...)` correctly make partner carrier/transfer choices explicit for Python reference, Triton, CuPy, and Numba?

Yes. `hit_stream_handoff.py:1005-1134` implements a branched dispatch that gives
each partner a distinct `status`, `carrier_protocol`, and `runtime_action`:

| Partner | Status (device-ready path) | Carrier protocol |
|---|---|---|
| `python_reference` | `host_reference_ready` | `host_columns` |
| `triton` (CAI needed) | `torch_carrier_preview` | `cuda_array_interface_to_torch_carrier` |
| `triton` (torch tensors) | `torch_carrier_preview` | `torch_tensor_carrier` |
| `cupy_conformance` | `descriptor_only` | `cuda_array_interface_descriptor` |
| `numba` (supported op) | `cuda_descriptor_preview` | `cuda_array_interface_descriptor` |

When inputs are not device-ready, all GPU-requiring partners flip to
`explicit_host_materialization_required` with `copy_or_host_stage_required = True`.
Unsupported partner/operation combinations produce `unsupported_fail_closed` with
`execution_allowed_without_copy = False`.

No implicit fallthrough between partners is present: each branch is entered
exclusively, and the status/carrier vocabularies are validated against their
respective constant tuples at lines 1099-1102 before the plan dict is returned.

### 2. Does the implementation preserve the v2.5 boundary that CuPy is currently descriptor-only for this generic hit-stream slice, while Triton/Numba remain preview-gated?

Yes.

**CuPy (lines 1074-1085):** `descriptor_only = True`,
`executable_preview_available = False`,
`runtime_action = "descriptor_only_no_generic_kernel_execution"`. The test at
`goal2740_hit_stream_cross_partner_transfer_plan_test.py:162-175` explicitly
asserts `assertFalse(plan["executable_preview_available"])` for CuPy.

**Triton (lines 1056-1073):** `status = "torch_carrier_preview"`,
`executable_preview_available = True`. The plan records that sm70 pod validation
is still required via `runtime_action =
"requires_sm70_pod_validation_before_performance_claim"` or
`"requires_torch_cuda_array_interface_adapter_and_pod_validation"`.

**Numba (lines 1086-1097):** `status = "cuda_descriptor_preview"`,
`executable_preview_available = True`,
`runtime_action = "numba_preview_requires_explicit_runtime_validation"`.
The `V2_5_NUMBA_PREVIEW_OPERATIONS` tuple in `v2_5_partner_support_matrix.py:29-32`
gates which operations reach this branch; others fall through to
`unsupported_fail_closed`.

The `V25PartnerSupportCell.__post_init__` in `v2_5_partner_support_matrix.py:56-78`
enforces at construction time that no support cell can set
`promoted_performance_path`, `rt_traversal_replacement_allowed`,
`public_speedup_claim_authorized`, or `true_zero_copy_claim_authorized` to True.
This structural guard is independent of the transfer plan logic.

### 3. Does the raw CUDA-array-interface hardening prevent fake/unproven pointers from being adapted at runtime without blocking hardware-proven native hit-stream columns?

Mostly yes, with one expected limitation.

The hardening in `gather_typed_payload_columns_for_hit_stream:790-803` adds a
guard specifically for the Triton path:

```python
if (
    bool(torch_carrier_adapter["raw_cuda_adapter_required"])
    and not bool(hit_stream_columns.native_device_column_output_proven_on_hardware)
    and not _all_torch_gather_columns(hit_stream_columns, payload_columns)
):
    raise ValueError(...)
```

This correctly blocks adaptation of raw CAI columns unless: (a) columns are
already torch tensors, or (b) `native_device_column_output_proven_on_hardware` is
explicitly True.

`RtdlRawCudaColumn.__cuda_array_interface__` (line 247-257) raises `RuntimeError`
if the owner's lifecycle state is `"closed"`. `RtdlNativeDeviceHitStreamOutput.to_handoff()`
(line 353-390) also fails if `closed` is True.

**Expected limitation:** `_torch_from_cuda_array_interface` (line 1577-1612)
validates dtype and device identity for zero-copy promotion, but does not
validate kernel-level pointer validity. The trust anchor for pointer legitimacy
is `native_device_column_output_proven_on_hardware`, which must be set by the
caller on hardware evidence. This is appropriate for planning-layer code and
consistent with prior goals.

### 4. Does the new plan avoid authorizing silent copies, true zero-copy claims, public speedup claims, or partner replacement of RTDL/OptiX traversal?

Yes, consistently:

- `silent_copy_forbidden: True` — hardcoded at line 1117, not conditional.
- `true_zero_copy_authorized: False` — hardcoded at line 1123.
- `public_speedup_claim_authorized: False` — hardcoded at line 1124.
- `stream_synchronization_required_for_zero_copy_claim: True` — line 1122.
- `claim_boundary` string is present (lines 1129-1133).
- `RT_TRAVERSAL_REPLACEMENT_ALLOWED` is imported from the partner continuation
  protocol; the support matrix `__post_init__` raises on any True value.

The continuation plan nesting at `plan_v2_5_hit_stream_partner_continuation:1152-1157`
calls `plan_v2_5_hit_stream_partner_transfer` and stores the result as
`partner_transfer_plan`. The outer continuation plan also sets
`true_zero_copy_authorized: False` and `public_speedup_claim_authorized: False`
independently (lines 1192-1193), so the claim boundaries are redundantly enforced
at both layers.

### 5. Are there code/test/report gaps that should block accepting Goal2740?

No gaps that should block acceptance. Specific observations:

**Coverage:** Seven tests cover Python reference (host-ready and device→requires
materialization), Triton (preview + CAI carrier), CuPy (descriptor-only), Numba
(preview), unsupported fail-closed nesting into the continuation plan, and the
non-star-export assertion. The test at line 209-211 verifies
`plan_v2_5_hit_stream_partner_transfer` is accessible as `rt.plan_v2_5_hit_stream_partner_transfer`
but absent from `rt.__all__`, matching the import at `__init__.py:147` with no
corresponding `__all__` entry.

**Pod validation:** The report records 41 tests passing on the pod at commit
`613f250e`. Commits `664dd32f` and `87770ba3` are documentation-only; no source
changes follow `613f250e`, so the pod results apply to the current state.

**Minor observation — CuPy non-device-ready carrier choice (lines 1074-1080):**
When `cupy_conformance` is selected but inputs are not device-ready, the carrier
is set to `cuda_array_interface_descriptor` with
`explicit_host_materialization_required`. The carrier label is technically moot
when a host stage is required first, but it is harmless — `execution_allowed_without_copy`
is `False` and `copy_or_host_stage_required` is `True`, so the app receives
correct execution guidance.

**Minor observation — `_all_seams_device_ready` with empty seams (line 1465-1471):**
Returns `False` for an empty seam list (`bool(seams) and all(...)`). This is a
safe default that will require explicit host materialization if the seam list is
unexpectedly empty.

## Risk List

1. **Preview gates are flag-only, not execution-layer enforced.** `executable_preview_available`
   and `descriptor_only` are advisory. A caller that ignores them and proceeds to
   `gather_typed_payload_columns_for_hit_stream` with Triton will attempt torch
   import and fail at runtime, not at the plan stage. This is expected behavior
   for a planning surface but means the plan output must be respected by callers.

2. **Triton/Numba preview status is not yet promoted.** Both partners require
   sm70 pod evidence before any public performance claim. The plan correctly
   records this via `runtime_action` fields, but promotion gates remain outside
   Goal2740's scope.

3. **Native release-entrypoint enforcement is still Python-side only.** As noted
   in Goal2739's boundary, native OptiX must still implement and validate the
   release ABI on hardware before the owner-lifecycle guard can be considered
   complete.

4. **Cross-GPU and multi-driver same-pointer evidence is unaddressed.** The
   existing zero-copy audit applies to single-GPU/single-driver configurations.
   Broader platform validation is out of scope for this goal.

5. **`_torch_from_cuda_array_interface` trusts pointer validity to the caller.**
   Raw CUDA pointer legitimacy relies on `native_device_column_output_proven_on_hardware`
   being set by a hardware-tested code path, not by Python introspection.

## Verdict

`accept-with-boundary`

Goal2740 correctly responds to the cross-partner transfer gap flagged in
Goal2739's boundary. It adds an explicit per-partner carrier/status plan,
preserves all v2.5 claim boundaries, keeps CuPy descriptor-only, keeps
Triton/Numba preview-gated, forbids silent copies unconditionally, and avoids
star-exporting the experimental planning surface.

The boundary: this is a contract/planning hardening, not a hardware promotion.
Triton and Numba remain preview-status. True zero-copy, public speedup claims,
and partner replacement of RTDL/OptiX traversal remain unauthorized. Native
release-entrypoint enforcement and cross-GPU validation are deferred to later
goals.
