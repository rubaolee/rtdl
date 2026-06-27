---

## Review: Phoenix V3 M56 LibRTS Set-B Metadata Diagnosis and Preflight Repair

**Date:** 2026-06-23
**Verdict:** `accept_m56_local_diagnosis_and_preflight_repair_no_pod_authorization`

---

### Question-by-Question Answers

**1. Is the diagnosis correctly scoped: productized runner executed, but metadata exposure/signature was insufficient?**

Yes. The M55 `summary.json` is unambiguous: all 16 current-side sample rows show `current_metadata_failures: ["set_b_control_candidate_missing"]` while simultaneously showing `fixture_contract_failures: []`, `prepared_execution_session_runner_used=true`, and `productized_execution_path=prepared_execution_session_runner`. The primitive contract strings (`generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count`, `generic_prepared_aabb_index_query_2d_count`) are correct. The runner was not skipped; only the metadata exposure was absent. The diagnosis scope is correct and tightly drawn.

The M55 preflight section in `summary.json` confirms the causal mechanism: the M47 harness as executed in M55 contained only `nvidia_smi`, `current_python_version`, `current_git_revision`, `current_preflight_tests`, `v2_python_version`, `v2_git_revision`. The `current_librts_set_b_source_signature` row is entirely absent — it did not exist at M55 run time. The preflight tests passed 43 tests, but those tests do not inspect whether the benchmark app propagates `set_b_control_candidate` into its output payload. That gap is the direct cause.

**2. Is it acceptable to treat stale or insufficiently source-signed target root as an inference from copied payloads rather than a fully proven remote-file fact?**

Acceptable, with the caveat that this must remain labeled as inference throughout. The alternative — that the source was correct but a runtime path-selection defect suppressed the field — cannot be ruled out from payload evidence alone. However: (a) the M56 `test_local_librts_runner_source_now_exposes_set_b_control_metadata` test verifies the local source chain end-to-end; (b) the signature script executed by `test_current_set_b_source_signature_preflight_passes_for_local_tree` returns `"failed": []` on the local tree; (c) no alternative runtime suppression path is suggested by the code. The inference is bounded, not overreached, and the M56 report labels it explicitly as inference. That epistemic honesty is the correct posture given we cannot inspect the remote POD files.

**3. Does the new `current_librts_set_b_source_signature` preflight materially prevent another M55-style paid run failure before samples execute?**

Yes, materially. The `CURRENT_SOURCE_SIGNATURE_SCRIPT` checks 8 specific markers:

- Function presence for both Embree count and OptiX prepared-query-set helpers in `prepared_execution.py`
- `metadata["set_b_control_candidate"] = True` appearing ≥3 times
- `metadata["set_a_probe_candidate"] = False` appearing ≥3 times
- `metadata["prepared_query_mode"] = "optix_prepared_query_set"` in the OptiX helper
- The benchmark app exposing `set_b_control_candidate` in its payload construction (≥2 occurrences, covering both payload-level and `prepared_execution_session_runner_metadata`)
- The benchmark app exposing `prepared_query_mode` into runner metadata

The row is `required=True`. The harness will exit before any measured sample runs if the script returns non-zero. If M55 had contained this preflight and the POD tree's benchmark app lacked the `set_b_control_candidate` exposure string, execution would have aborted at preflight. This is a genuine gate, not theater.

**Residual weakness here:** the check is static source-string matching, not a runtime assertion. A code path that conditionally suppresses the metadata at execution time despite correct source strings would pass the preflight but still yield a missing field at runtime. That scenario is not suggested by the current code structure, but the gap exists.

**4. Does the repair avoid changing M55 evidence or claiming watch-row closure?**

Yes, cleanly. The M55 evidence directory is read-only in M56. More importantly, `test_m55_red_payloads_used_productized_runner_but_lacked_set_b_metadata` positively asserts `assertIsNot(metadata.get("set_b_control_candidate"), True)` against the copied M55 payloads — this test will fail if anyone retroactively modifies M55 files to show the field as present. Both watch rows remain `red_failure_watch_row_open`. The report, the test, and the harness are all consistent on this point.

No watch-row closure is asserted anywhere in M56. The M56 report explicitly states: "This does not close either LibRTS watch row." The locked-red test is the stronger guarantee.

**5. Are the new tests sufficient for local completion of M56?**

Yes, for the local scope. The combined test surface covers:

- M55 red state locked (M56 diagnosis test, test 1)
- New preflight row exists, is required, and contains the target field names (M56 diagnosis test, test 2; M47 protocol test, `test_dry_run_includes_preflight_plan_without_authorization`)
- Local source now has all required markers (M56 diagnosis test, test 3)
- Signature script actually executes and passes on the local tree (`test_current_set_b_source_signature_preflight_passes_for_local_tree` — this is the most important test, it runs the subprocess and checks `"failed": []`)
- Full v3_rebuild (656 tests, 129 modules) passes

What is intentionally absent — and correctly so — is any test claiming the signature-checked source would produce passing metadata at POD runtime. That requires a new authorized run, not local tests.

**6. Is the next allowed action external completion audit and, only later, a separate reviewed authorization packet if another POD run is needed?**

Yes, and the documents are correctly sequenced. The M55 3-AI consensus (M55 goal completion document) authorized local diagnosis as the next step. M56 performs exactly that and stops. M56 explicitly requires "a separate reviewed authorization packet" before any future M47 run. The M56 report does not contain any token, authorization language, or claim that would permit a run. The sequence is: this review → acceptance → external completion audit → (if warranted) separate authorization packet.

---

### Non-Authorization Verification

All ten preserved non-authorizations are confirmed intact across all reviewed documents:

| Boundary | Status |
|---|---|
| No V3 release | Confirmed |
| No all-app benchmark run | Confirmed |
| No broad paid POD campaign | Confirmed |
| No second M47 run | Confirmed |
| No public speedup wording | Confirmed |
| No broad V3-over-V2 claim | Confirmed |
| No V4 work | Confirmed |
| No embedding | Confirmed |
| No C ABI | Confirmed |
| No true zero-copy claim | Confirmed |
| No watch-row closure | Confirmed |

---

### Residual Risks (Acceptance Conditions)

Three risks survive acceptance and must be carried into any future authorization request:

**Risk 1 — Static vs. dynamic check gap.** The `current_librts_set_b_source_signature` script verifies source strings, not runtime behavior. A future run must still validate that `set_b_control_candidate=True` appears in actual execution payloads, not only in source. The new metadata-failure classification logic in `current_metadata_failures()` (lines 515–533 of the harness) handles this at analysis time, which closes the loop — but only if the run is not aborted for another reason first.

**Risk 2 — M55 embree timing is materially below threshold even setting aside the metadata failure.** Embree geomean is 0.932, pass count 4/8. If a future run produces correct metadata, the embree scenario may still classify as `red_failure_watch_row_open` on timing grounds. Fixing the metadata does not guarantee green. This is not a defect in M56, but it must not be forgotten when framing a future authorization request.

**Risk 3 — Unproven POD tree state.** We cannot confirm whether the M55 POD tree had a stale benchmark app or a correct-source/broken-propagation bug. The repair addresses both symptoms via the source-signature gate, but the root cause remains inferred. If the M55 failure was a runtime propagation bug rather than a stale file, the source-signature check would not have been sufficient alone and additional testing of the runtime path would be required before a new run is authorized.

---

### Verdict

**`accept_m56_local_diagnosis_and_preflight_repair_no_pod_authorization`**

The diagnosis is credibly scoped, the inference is appropriately bounded, the new preflight check is a genuine gate against the specific M55 failure mode, M55 evidence is preserved and locked red, the tests are sufficient for local completion, and no non-authorization boundary is breached. The three residual risks above must be addressed in any future authorization packet requesting a new M47 POD run.
