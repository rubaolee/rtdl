# Antigravity Review: Phoenix V3 M57 Source-Signature-Gated LibRTS Rerun Authorization after Fail-Closed Fix

**Date:** 2026-06-23  
**Reviewer:** Antigravity (independent external review)  
**Candidate packet:** [call_for_review_phoenix_v3_m57_source_signature_gated_librts_rerun_authorization_2026-06-23.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reviews/call_for_review_phoenix_v3_m57_source_signature_gated_librts_rerun_authorization_2026-06-23.md)

---

## Verdict

**authorize_m57_one_source_signature_gated_librts_rerun_after_fail_closed_fix**

---

## Authorization Token and Execution Preconditions

### Exact Token
```text
M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED
```

### Exact Preconditions

The executor must satisfy all conditions below:

1. **Target Dry-Run Verification**: Run the stability protocol script on the target POD machine first without the `--execute` flag to conduct a dry-run:
   `py -3 scripts/v3_phoenix_m47_librts_stability_protocol.py --v2-root <path_to_v2_14>` (or using explicit python paths).
2. **Preflight Error Check**: Verify that the dry-run output contains `failed_checks: []` (no checks failed).
3. **Source-Signature Gate Validation**: Confirm that the dry-run preflight row `current_librts_set_b_source_signature` reports `returncode: 0` and that its stdout contains `"failed": []`. If this preflight check fails or is missing, stop immediately; do not proceed to execution, and copy back the failed dry-run evidence.
4. **Authorized Run Execution**: Only if both preconditions (2) and (3) are satisfied, execute exactly one run of the stability script on the target POD machine with the authorization token:
   `py -3 scripts/v3_phoenix_m47_librts_stability_protocol.py --execute --authorization-token M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED --v2-root <path_to_v2_14>`
5. **Narrow Scope Enforcement**: The execution must use the unchanged M47 scenario set: `optix_cold_single_shot` and `embree_32768_stress`. It must use exactly 8 paired samples per scenario, real roots (no placeholders), and explicit target/V2 Python paths.
6. **No Raw Watch-Row Closures**: Copy back the full execution evidence including `summary.json`, `README.md`, all stdout/stderr files, preflight files, and driver logs. Do not close watch rows from raw run output. The copied evidence must be interpreted only via a later review packet.

---

## Findings

**P0 Findings (Blockers): None**

**P1 Findings (Requirements before run): None**

**P2 Findings (Notes):**
- **Residual Risks:**
  1. The preflight check is a static source-signature check on files, not a runtime verification of executed code. The future payload must still be verified for `set_b_control_candidate=true` at runtime.
  2. The rerun may still be performance-red (e.g., the M55 Embree watch row was previously performance-red). Resolving the metadata issue is necessary but not sufficient for achieving performance conformance.
  3. The exact root source state is inferred rather than directly proven.

---

## Audit Checklist & Answers to Review Questions

**1. Does the M47 harness now abort before measured samples when preflight returns errors?**  
Yes. In [v3_phoenix_m47_librts_stability_protocol.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/scripts/v3_phoenix_m47_librts_stability_protocol.py#L166-L175), the `build_or_run_packet` function executes `execute_preflight(args)`. If `preflight_errors` contains any errors, it immediately returns a payload with `scenario_results={}`, `run_errors=preflight_errors`, and `status=STATUS_FAILED`, preventing execution from reaching `execute_schedule()`.

**2. Does the test suite cover that fail-closed behavior?**  
Yes. The test case [test_execute_aborts_before_samples_when_preflight_fails](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v3_phoenix_m47_librts_stability_protocol_test.py#L137-L171) in [v3_phoenix_m47_librts_stability_protocol_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v3_phoenix_m47_librts_stability_protocol_test.py) patches `execute_preflight` to return preflight errors and asserts that `execute_schedule` is not called, the status is set to `STATUS_FAILED`, the errors are captured, and no scenario results are recorded.

**3. Is the M57 packet narrow enough: one run, unchanged scenarios, exactly 8 paired samples, real roots, explicit Python paths, target dry-run first, source-signature gate required?**  
Yes. All parameters are tightly constrained:
- Exactly one execution of `scripts/v3_phoenix_m47_librts_stability_protocol.py` is authorized.
- The scenarios are unchanged: `optix_cold_single_shot` and `embree_32768_stress` (hardcoded in `SCENARIOS`).
- Exactly 8 paired samples per scenario (validated via `validate_args`).
- Real roots (v2-root is checked and required on execute).
- Explicit target/V2 Python paths via arguments.
- Target dry-run first, requiring validation of `failed_checks=[]` and the source-signature gate (`current_librts_set_b_source_signature`).

**4. Does the new token avoid reusing the consumed M54/M55 token?**  
Yes. The token `M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED` is distinct from the previously consumed token `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`.

**5. Are the residual risks preserved, especially that a metadata-fixed run may still be performance-red?**  
Yes. Residual risks are carried forward and acknowledged in full, including the risk that the watch rows may remain performance-red on Embree or Optix.

**6. Does this review avoid authorizing release, all-app, public claims, V4, embedding, C ABI, true-zero-copy, watch-row closure, scenario/sample changes, or a second run?**  
Yes. None of these boundaries are authorized. All are explicitly quarantined.

---

## Non-Authorization Boundaries

This review explicitly does **NOT** authorize:
- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure
- no scenario changes
- no sample-count changes
- no second M57 run
