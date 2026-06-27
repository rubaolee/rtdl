I now have all the evidence. Let me render the verdict.

---

## Phoenix V3 M57 — Source-Signature-Gated LibRTS Rerun Authorization Review

**Verdict: `authorize_m57_one_source_signature_gated_librts_rerun`**

---

### 1. Does M56 provide enough local repair evidence to justify exactly one source-signature-gated rerun?

**Yes.** The evidence chain is complete and internally consistent. M55 produced valid red/open evidence with a specific, narrow failure: `set_b_control_candidate_missing`. M56 read the copied M55 payloads, confirmed the productized prepared-execution-session runner *did* execute (both scenarios), and correctly narrowed the failure to metadata exposure rather than path skipping. The added `current_librts_set_b_source_signature` preflight checks all eight required markers directly in source files. The focused test `test_current_set_b_source_signature_preflight_passes_for_local_tree` confirms the local tree passes. All 3-AI seats accepted M56. A rerun is the minimum necessary next step to determine whether the metadata repair holds under POD execution.

---

### 2. Are the M57 execution conditions narrow enough to prevent another broad POD campaign?

**Yes, with one code-level gap noted (non-blocking).** The conditions enforce: one run only, unique token, unchanged scenario set, exactly 8 samples (harness enforces via `validate_args`), all-false `CLAIM_BOUNDARY` (hardcoded), dry-run first, and source-signature gate. These are tight.

**Code-level gap:** `build_or_run_packet` calls `execute_preflight` then unconditionally calls `execute_schedule` — if the source-signature preflight fails during execution, the harness still proceeds to run measured samples. It records the preflight error in `run_errors`, which populates `failed_checks`, which exits 2, but measured samples are already executed. The protocol's "stop immediately if source-signature fails" is procedurally enforced through the dry-run gate, not by a code abort mid-run.

This is non-blocking because: (a) the dry-run gate is the primary defense — the executor must verify `failed_checks=[]` *and* confirm `current_librts_set_b_source_signature` passes before starting execution; (b) the non-authorization section explicitly blocks watch-row closure from raw output; (c) any evidence from a failed-preflight execution would be flagged in `failed_checks` and would require a subsequent review packet before interpretation.

---

### 3. Does the proposed token avoid reusing the consumed M54/M55 token?

**Yes.** The consumed token is `M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED`. The M57 token is `M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED`. These are distinct strings. The M55 3-AI consensus explicitly records the old token as consumed.

**Secondary note:** The old token remains in `AUTHORIZED_EXECUTION_TOKENS` alongside the new one. This is a protocol-only control; the harness does not enforce token consumption. The review chain is the consumption record. This is a known design property, not a defect introduced in M57.

---

### 4. Does the required `current_librts_set_b_source_signature` dry-run preflight adequately address the known M55 metadata failure before measured samples?

**Yes.** The eight checks in `CURRENT_SOURCE_SIGNATURE_SCRIPT` directly target each field that was missing at M55 runtime:

| Check | Addresses M55 failure? |
|---|---|
| `prepared_embree_count_helper_present` | Yes — confirms AABB Embree path exists |
| `prepared_optix_query_set_helper_present` | Yes — confirms OptiX path exists |
| `prepared_helpers_mark_set_b_control` (≥3 occurrences) | Yes — directly targets the missing `set_b_control_candidate=true` |
| `prepared_helpers_mark_not_set_a_probe` (≥3 occurrences) | Yes — confirms Set-A exclusion |
| `prepared_optix_helper_marks_prepared_query_mode` | Yes — OptiX field that was missing |
| `librts_app_exposes_payload_set_b` | Yes — runtime payload exposure |
| `librts_app_exposes_metadata_set_b_twice` (≥2 occurrences) | Yes — both top-level and nested metadata |
| `librts_app_exposes_optix_prepared_query_mode` | Yes — runner metadata exposure |

This is a material improvement over M54/M55, which relied on named unittest modules that could pass against a stale benchmark app. The source-signature check inspects the exact text of the files the benchmark app executes.

Acknowledged limitation (from M56 consensus, correctly carried forward): this is static source-string checking, not runtime proof. Future execution payloads must still emit `set_b_control_candidate=true` for the metadata check to clear. A runtime propagation defect could theoretically survive this gate.

---

### 5. Are the residual risks from M56 carried forward, especially that a metadata-fixed rerun may still be performance-red?

**Yes, all three M56 residual risks are correctly carried forward:**

1. **Static-only preflight.** Source-string inspection does not prove runtime emission. A defect in how the benchmark app reads or propagates the metadata at runtime could still produce missing fields under POD.

2. **Metadata repair does not guarantee green.** The M55 Embree geomean was `0.931885x` with `4/8` passing at ≥0.95. Even with `set_b_control_candidate_missing` cleared, the Embree scenario may still classify as `red_failure_watch_row_open` on performance grounds. The OptiX geomean was `0.984404x` with `6/8` pass; after metadata repair it would likely clear to `yellow_stability_boundary_watch_row_open` (≥0.95 geomean but unlikely to satisfy the ≥7/8 pass and ≥0.98 stripped geomean for green). Executors must not interpret a post-rerun result as success without a subsequent review packet.

3. **M55 target tree state remains inferred.** A stale target current root is the plausible hypothesis, but a runtime metadata propagation defect cannot be fully ruled out without the rerun itself.

---

### 6. If authorized, is the next allowed action only target dry-run, then exactly one execution if the dry-run passes?

**Yes.** The M57 packet conditions 7–12 sequence this correctly. The harness enforces dry-run mode by default (requires explicit `--execute`) and requires the authorization token for execution. The procedural requirement to gate on `failed_checks=[]` in the dry-run and to confirm `current_librts_set_b_source_signature` passes before proceeding is unambiguous. No watch-row closure or claim interpretation is allowed from raw run output.

---

### Authorized Token

```text
M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED
```

### Exact Preconditions

1. Run `scripts/v3_phoenix_m47_librts_stability_protocol.py` **without** `--execute` (target dry-run) on the POD machine.
2. Confirm the dry-run output has `failed_checks: []`.
3. Confirm the dry-run preflight row `current_librts_set_b_source_signature` has `returncode: 0` and its stdout contains `"failed": []`. If it fails: **stop. Do not proceed to execution. Copy back the failed dry-run evidence.**
4. Only if both conditions above are satisfied: run again with `--execute --authorization-token M57_SOURCE_SIGNATURE_GATED_M47_RERUN_AUTHORIZED`.
5. Use the unchanged M47 scenario set: `optix_cold_single_shot` and `embree_32768_stress`.
6. Use exactly 8 paired samples per scenario.
7. Use real current and V2.14 roots; use explicit Linux/POD Python paths.
8. Copy back full evidence: `summary.json`, `README.md`, all measured `stdout.json` and `stderr.txt` files, all preflight files, and driver logs.
9. Do not close any watch rows from raw run output. Interpret evidence only through a later review packet.

### Residual Risks

- **Performance still red.** A metadata-fixed rerun is not predicted to be green. Embree timing was materially below threshold in M55 even before accounting for the metadata failure. A red result after M57 is a valid outcome.
- **Runtime propagation not proven.** The static source-signature preflight does not guarantee the POD benchmark app emits the correct fields at runtime. A runtime defect would produce the same `set_b_control_candidate_missing` label even if the source checks pass.
- **Harness does not abort on mid-execution preflight failure.** If source-signature fails during `--execute`, measured samples still run. The executor must not interpret or rely on those samples.
- **No second M57 run.** This token is consumed on first use. No follow-on rerun is authorized by this review.

### Non-Authorization

This review does not authorize: V3 release, all-app benchmark run, broad paid POD campaign, public speedup wording, broad V3-over-V2 claim, V4 work, embedding, C ABI, true zero-copy claim, watch-row closure, scenario changes, sample-count changes, or a second M57 run.
