# Goal3133: Claude Independent Review — v2.8 Partner Front-Door Chain (Goals 3108–3131)

Date: 2026-06-03

Reviewer: Claude (claude-sonnet-4-6), independent

Verdict: **accept-with-boundary**

---

## Summary

The v2.8 Goals 3108–3131 chain is internally consistent and correctly scoped as
a development-phase contract foundation. The app-agnostic engine boundary is
preserved throughout. The front door rejects hidden dispatch and auto partner
selection at every layer. Local functional coverage is complete for all seven
currently supported partner-front-door operations through at least one healthy
explicit partner. No bugs that invalidate the chain were found.

Four medium observations and two low observations are recorded below. None
require rework before continuing development, but the two medium semantic gaps
(top-k ordering direction and missing partner smoke for `segmented_min_f64` /
`segmented_max_f64`) should be documented before any operation-surface claim is
made.

---

## Findings by Severity

### Medium

**M1 — `grouped_topk_f64` ordering direction is undocumented**

In `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py` lines 233–236:

```python
result = rt.execute_segmented_typed_stream_reference_continuation(adapter, k=1)
self.assertEqual(result["outputs"]["group_ids"], [0])
self.assertEqual(result["outputs"]["item_ids"], [10])
self.assertEqual(result["outputs"]["scores"], [1.5])
```

Input data: `((0, 10, 1.5), (0, 11, 2.5))`. Group 0 contains item 10 (score
1.5) and item 11 (score 2.5). With k=1, the reference returns item 10 (the
*lower* score), not item 11 (the higher). In a spatial nearest-neighbor context,
"top-k" is naturally ascending (smallest distance = best), and that interpretation
is consistent with this result. However, the stream contract, continuation plan,
and report vocabulary do not explicitly state the ordering direction. Any future
partner implementation that interprets "top-k" as descending will produce
silently wrong results. The direction should be documented as part of
`V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS` or in the operation-level
boundary comment.

**M2 — `segmented_min_f64` and `segmented_max_f64` have no partner-consumer smoke**

Both operations appear in `V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS`
(`src/rtdsl/v2_8_typed_result_stream.py` line 49–50) and are handled by the
reference consumer path in `_reference_inputs_for_plan`
(`src/rtdsl/v2_8_segmented_typed_stream_adapter.py` lines 527–529), but both are
absent from `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS`
(line 27–35) and have no local Linux smoke anywhere in the Goals 3120–3131
chain. The coverage table in Goal3131 omits them entirely. This is not a blocker
for the chain as development work, but before any operation-surface comparison
claim is made the table should either show smoke evidence for these two
operations or explicitly record them as not-yet-covered.

**M3 — `grouped_argmin_f64` and `grouped_argmax_f64` partner output schema not explicitly canonicalized**

In `_execute_partner_front_door`
(`src/rtdsl/v2_8_segmented_typed_stream_adapter.py` lines 629–638):

```python
if operation == "grouped_argmin_f64":
    from .partner_adapters import grouped_argmin_f64_partner_columns
    result = grouped_argmin_f64_partner_columns(..., return_metadata=True)
    return result["columns"], dict(result["metadata"])
```

The `result["columns"]` value from the helper is returned directly. By contrast,
`bounded_collect_finalize_i64` (lines 665–671) performs an explicit
`canonical_columns` filter before returning, blocking auxiliary keys such as
`counts` from leaking through. If either grouped-arg helper ever returns extra
keys (e.g., an intermediate `row_offsets`), those keys would pass through the
front door without a schema check. The Torch smoke (Goal3129) passed in
practice, but the absence of an explicit canonicalization step is an asymmetry
that should be addressed before these paths carry stronger output-contract claims.

**M4 — `compact_mask_i64` asymmetry between reference consumer and partner front door is undocumented**

`compact_mask_i64` is included in `V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS`
and is fully handled by `_reference_inputs_for_plan`, but it is explicitly absent
from `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS`. The
test for this case (`test_partner_consumer_dry_run_marks_unsupported_operation`
lines 395–423) correctly verifies that the dry-run marks the operation as
unsupported. However, none of the reports (Goals 3114, 3117, 3122, 3125, 3128,
3131) explain *why* `compact_mask_i64` is excluded from the partner front door
when the reference consumer supports it. The rationale should be documented to
prevent a future contributor from adding partner support without understanding
whether the operation is excluded by design (no group semantics) or simply
deferred.

### Low

**L1 — `user_selected_partner` sentinel is valid by the validator but semantically misleading**

The default value `"explicit_user_choice_required"` in `V28GroupedContinuationPlan`
(`src/rtdsl/v2_8_typed_result_stream.py` line 215) passes the validator because
it is neither `""` nor `"auto"`. A caller who forgets to set a real partner name
will not receive a validation error; the plan will silently carry the sentinel
string as its partner. The guards at `plan_segmented_typed_stream_partner_continuation`
and `execute_segmented_typed_stream_partner_continuation` do catch `""` and
`"auto"` but not the sentinel. Consider adding the sentinel string to the
rejection list in `validate_grouped_continuation_plan`, or using a stricter
allowlist approach.

**L2 — `_adapter_like` silently swallows arbitrary exceptions**

`_adapter_like` (`src/rtdsl/v2_8_segmented_typed_stream_adapter.py` lines 708–717)
catches a bare `except Exception` when accessing `.shape[0]`. A malformed tensor
object that raises an unexpected error will silently produce an empty tuple,
making the `group_count` heuristic in `_resolve_group_count` return 0 rather than
surfacing the error. In the current usage this is benign since the function is
only called for bridge metadata row-count estimation. However, the silent failure
mode is worth noting for future callers.

---

## Claim Boundary Assessment

The claim boundary is correctly and consistently implemented.

Seven boolean flags (`app_specific_engine_logic_allowed`,
`automatic_partner_selection_allowed`, `hidden_dispatch_allowed`,
`release_authorized`, `public_speedup_claim_authorized`,
`rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`) are
enforced as permanently `False` via `__post_init__` guards that raise `ValueError`
on any `True` value. These guards are present in all three contract-bearing
classes: `V28TypedResultStreamContract`, `V28GroupedContinuationPlan`, and
`V28SegmentedTypedStreamAdapterResult`.

Three additional promotion flags (`native_producer_promoted`,
`partner_consumer_promoted`, `device_resident_result_stream_proven`) are
similarly locked to `False` in the adapter result.

The `V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY` and
`V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY` string constants propagate
through `to_metadata()` outputs and through every execution-result dict.

All four consensus reports (Goals 3122, 3125, 3128, 3131) repeat a consistent
"Still Not Authorized" block. No report contradicts any other.

---

## Files Inspected

| File | Role |
| --- | --- |
| `src/rtdsl/v2_8_typed_result_stream.py` | Core stream/continuation contract (Goal3108) |
| `src/rtdsl/v2_8_segmented_typed_stream_adapter.py` | Reference adapter and partner front door (Goals 3111, 3114, 3117, 3123, 3126) |
| `tests/goal3108_v2_8_typed_result_stream_contract_test.py` | Contract unit tests |
| `tests/goal3111_v2_8_segmented_typed_stream_adapter_test.py` | Adapter / front-door / smoke unit tests |
| `docs/reports/goal3108_v2_8_typed_result_stream_contract_2026-06-03.md` | Goal3108 report |
| `docs/reports/goal3111_v2_8_segmented_typed_stream_adapter_2026-06-03.md` | Goal3111 report |
| `docs/reports/goal3114_v2_8_reference_grouped_continuation_consumer_2026-06-03.md` | Goal3114 report |
| `docs/reports/goal3117_v2_8_explicit_partner_consumer_front_door_2026-06-03.md` | Goal3117 report |
| `docs/reports/goal3122_v2_8_cupy_partner_consumer_local_linux_smoke_2ai_consensus_2026-06-03.md` | 2-AI consensus for Goal3120 CuPy smoke |
| `docs/reports/goal3125_v2_8_partner_consumer_named_output_hardening_2ai_consensus_2026-06-03.md` | 2-AI consensus for Goal3123 named-output hardening |
| `docs/reports/goal3128_v2_8_torch_partner_front_door_and_numba_boundary_2ai_consensus_2026-06-03.md` | 2-AI consensus for Goal3126 Torch smoke and Numba boundary |
| `docs/reports/goal3131_v2_8_torch_grouped_arg_front_door_local_smoke_2ai_consensus_2026-06-03.md` | 2-AI consensus for Goal3129 Torch grouped-arg smoke |

---

## Answers to Review Questions

**Q1. Does the v2.8 chain preserve the app-agnostic engine boundary?**

Yes. The typed stream vocabulary uses generic terms: `group_key`, `item_id`,
`score`, `payload`, `mask`, `witness`, `row_offset`. Stream kinds are
structural, not benchmark-app-specific (`hit_stream`, `candidate_stream`,
`ranked_summary_stream`, `bounded_witness_stream`, `grouped_reduction_stream`).
No benchmark-application names appear in the contract classes or exported
constants.

**Q2. Does the front door require explicit user partner selection and reject hidden dispatch / auto partner selection?**

Yes, at four independent enforcement points:

1. `V28GroupedContinuationPlan.__post_init__` rejects `""` and `"auto"` values
   for `user_selected_partner`.
2. `plan_segmented_typed_stream_partner_continuation` raises `ValueError` for
   `""` and `"auto"` before any execution.
3. `execute_segmented_typed_stream_partner_continuation` requires caller-supplied
   `partner_columns`; missing columns raise `ValueError` with
   "no hidden host materialization" in the message.
4. The `automatic_partner_selection_allowed` and `hidden_dispatch_allowed`
   boolean flags are locked `False` in the contract and raise `ValueError` if set
   `True`.

Note finding L1: the sentinel default `"explicit_user_choice_required"` is not
itself rejected, which is a minor gap.

**Q3. Are actual partner outputs now schema-consistent with the reference consumer for the covered operations?**

For the three CuPy operations (`segmented_count_i64`, `segmented_sum_f64`,
`grouped_vector_sum_f64x2`): yes, the named output shapes were hardened in
Goal3123 and verified with local Linux smoke.

For `bounded_collect_finalize_i64`: yes, the output was normalized to canonical
columns `{group_ids, item_ids, row_offsets}` in Goal3126 and a regression test
blocks auxiliary `counts` from leaking.

For `grouped_argmin_f64`, `grouped_argmax_f64`, `grouped_topk_f64`: local Torch
smoke (Goal3129) matched the Python reference consumer in practice, but the
front door returns `result["columns"]` from the helper without an explicit
canonicalization step (M3 above). Schema consistency is confirmed empirically
but not structurally enforced for these three operations.

For `segmented_min_f64`, `segmented_max_f64`: no partner-consumer smoke exists.
Consistency with the reference consumer is unverified.

**Q4. Is local functional coverage correctly bounded, including the Numba local CUDA-stack boundary?**

Yes. The Numba boundary is correctly classified as a local-host CUDA-stack
failure (CUDA_ERROR_CONTEXT_IS_DESTROYED for a trivial independent kernel, not
an RTDL failure). The GTX 1070 / local Linux host boundary is consistently
stated in all four consensus reports. The coverage table in Goal3131 accurately
reflects seven operations passing through at least one healthy partner, with
Numba-specific grouped-arg validation still open.

**Q5. Are the claim boundaries clear: no release, no speedup, no broad RT-core, no true-zero-copy, no app-specific engine, no user-defined shader injection?**

Yes. All six prohibited claims are:

- Blocked by `False` default values on named boolean fields.
- Guarded by `__post_init__` that raises `ValueError` if any flag is set `True`.
- Propagated through `to_metadata()` and all execution-result dicts.
- Carried as text constants (`V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY`,
  `V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY`) in every metadata
  payload.
- Consistently repeated in every consensus document's "Still Not Authorized"
  section.

**Q6. What must be done next before v2.8 can make stronger claims?**

In roughly ascending order of effort:

1. **Document `grouped_topk_f64` ordering direction** (ascending = lowest k
   scores) in the contract or at minimum in the operation-level docstring.
   Unambiguous semantics are required before any partner implementation targets
   this operation without access to the reference test.

2. **Resolve `compact_mask_i64` asymmetry**: document why it is reference-only
   and whether a partner-front-door path is deferred or excluded by design.

3. **Add explicit canonicalization** for `grouped_argmin_f64` and
   `grouped_argmax_f64` partner outputs, paralleling what Goal3126 did for
   `bounded_collect_finalize_i64`.

4. **Close `segmented_min_f64` / `segmented_max_f64` coverage**: either add
   partner-consumer support and smoke evidence, or record these operations as
   explicitly deferred in the coverage table.

5. **Numba-specific grouped-arg validation** on a healthy CUDA stack. Torch
   passing does not close Numba; they use different compilation paths.

6. **Pod-class hardware** for any timing or performance evidence. The GTX 1070
   local Linux host is correctly classified as a functional-smoke host, not a
   performance host. Any performance or speedup claim requires pod-class hardware
   and larger stream sizes.

7. **Release and public-speedup claims remain fully blocked** until items 1–6
   above are addressed and a full pod-class validation sweep is completed.

---

## Verdict

**accept-with-boundary**

The v2.8 Goals 3108–3131 chain is accepted as an internal development-phase
contract foundation with local functional smoke. The app-agnostic engine
boundary is preserved. The partner-selection enforcement is structurally sound
at four independent layers. Local functional correctness coverage is complete for
all seven currently supported partner-front-door operations through at least one
healthy explicit partner. Claim boundaries are machine-checkable and consistently
documented.

The chain does not authorize release, public speedup, broad RT-core wording,
true-zero-copy wording, hidden dispatch, automatic partner selection,
app-specific native-engine behavior, or user-defined shader injection. The four
medium observations above should be addressed before any operation-surface
comparison or partner-coverage claim is published.
