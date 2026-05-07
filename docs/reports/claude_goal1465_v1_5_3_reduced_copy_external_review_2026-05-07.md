---

## Verdict

**ACCEPT_WITH_NOTES**

The v1.5.3 reduced-copy artifacts are accurately bounded as internal reduced-copy candidate evidence only. All six prohibited claim categories are absent from code, tests, and reports. Three minor textual gaps in partner-tensor-handoff coverage are noted but do not constitute violations.

---

## Evidence Checked

**`src/rtdsl/v1_5_3_reduced_copy.py`**

| Check | Result |
|---|---|
| `true_zero_copy_authorized` = False on all three functions | Pass |
| `public_speedup_wording_authorized` = False on all three functions | Pass |
| `whole_app_speedup_claim_authorized` = False on all three functions | Pass |
| `stable_public_primitive_authorized` = False on all three functions | Pass |
| `release_action_authorized` = False on all three functions | Pass |
| `validate_v1_5_3_reduced_copy_contract` hard-fails if any flag is not False | Pass |
| `V1_5_3_REDUCED_COPY_BLOCKED_CLAIMS` contains all five prohibited categories | Pass |
| `V1_5_3_REDUCED_COPY_FORBIDDEN_WORDING` lists "true zero-copy", "zero-copy speedup", "whole-app acceleration", "public speedup", "release-ready" | Pass |
| `V1_5_3_REDUCED_COPY_MISSING_EVIDENCE` retains `embree_optix_same_contract_parity_where_claimed` and `external_ai_review_before_public_claims` | Pass |
| Contract `claim_boundary` text explicitly excludes true zero-copy, public speedup, whole-app claims, stable primitive promotion, partner tensor handoff, and release action | Pass |
| `prepare_collect_k_i64_host_input_buffer` docstring: "not a zero-copy path" | Pass |
| `prepare_collect_k_i64_host_input_buffer` claim_boundary: "still copies user rows into ctypes host storage" | Pass |
| `run_native_collect_k_bounded_with_typed_host_buffers` claim_boundary: "still uses host ctypes storage" | Pass |
| `measure_collect_k_typed_host_input_reuse`: `timing_recorded_for_diagnostics_only = True`; `claim_boundary` says "Timing is diagnostic only" | Pass |
| Measurement fields `baseline_input_materialization_count = iterations`, `typed_input_materialization_count = 1` consistent with code logic | Pass |

**`src/rtdsl/__init__.py`**

All v1.5.3 symbols exported without modification or additional wording. No claim-boundary text added at the `__init__` layer.

**Tests (goals 1461–1464)**

| Test file | Key assertions |
|---|---|
| `goal1461` | Verifies `missing_evidence` contains backend parity and external review; all five authorization flags are False; forbidden wording includes "true zero-copy" and "public speedup" |
| `goal1462` | Verifies `copy_boundary = "typed_contiguous_host_buffer"`; `materialized_nested_python_rows_present = False`; all five flags are False; claim_boundary contains "still copies user rows into ctypes host storage" |
| `goal1463` | Verifies `true_zero_copy_authorized` and `public_speedup_wording_authorized` are False; confirms input/output buffer addresses are passed to native symbol |
| `goal1464` | Verifies `timing_recorded_for_diagnostics_only = True`; all five flags are False; claim_boundary contains "Timing is diagnostic only"; materialization count delta is correct |

**Reports (goals 1461–1464)**

All four reports state boundary exclusions. Goals 1461, 1462, and 1463 explicitly name all six prohibited items including "partner tensor handoff." Goal 1464 names five (omits "partner tensor handoff" — see Notes).

---

## Blockers

None.

---

## Notes

1. **`validate_v1_5_3_reduced_copy_contract` does not assert the "partner tensor handoff" phrase.** The contract `claim_boundary` text currently includes "partner tensor handoff," but the validator's phrase-check loop (`v1_5_3_reduced_copy.py:116–125`) does not verify that phrase. If the phrase is later removed from the text, no validator will catch the regression.

2. **Three per-function `claim_boundary` texts omit "partner tensor handoff".** The functions `prepare_collect_k_i64_host_input_buffer` (line 180–186), `run_native_collect_k_bounded_with_typed_host_buffers` (line 347–354), and `measure_collect_k_typed_host_input_reuse` (line 446–452) each list five excluded claim types but not "partner tensor handoff." None of these functions make the claim; the omission is a coverage gap, not a violation.

3. **Goal1464 report boundary section omits "partner tensor handoff".** The boundary paragraph in `goal1464_v1_5_3_typed_host_input_measurement_2026-05-07.md` lists five exclusions and does not enumerate "partner tensor handoff." The code enforces the exclusion; the report text is incomplete relative to the other three reports.

None of items 1–3 constitute a current boundary violation. All are textual/validation robustness gaps that could be tightened before any further promotion.
