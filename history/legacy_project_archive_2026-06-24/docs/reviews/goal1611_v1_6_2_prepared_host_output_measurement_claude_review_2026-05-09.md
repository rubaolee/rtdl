---

## Review: Goal1611 / v1.6.2 Prepared Host-Output Measurement Preflight

### Verdict

**ACCEPTED** as a local prepared-host-output measurement preflight. No required fixes.

---

### Findings

**Schema Reuse**

Complete and correct. `CLAIM_FLAGS`, `PHASE_FIELDS`, and `COPY_COUNT_FIELDS` are all sourced from Goal1610 (`script:28`, `manifest:98–107`). `validate_record()` chains to `goal1610.validate_record()` (`script:246`), so the parent schema's invariants remain enforced. The `output_contract` field is explicitly set to `"goal1610_phase_copy_record"` in both the manifest and every record. The JSON artifact's phase and copy-count field lists match the Goal1610 canonical lists exactly.

**Materialization Counters**

Semantically correct and test-verified. With `iterations=3`: baseline materializes 3 times (one per call), prepared materializes once and reuses the buffer, delta is 2. The test pins these exact values (`test:55–65`). `prepared_buffer_reuse_count` equals `iterations` in both script and artifact. Device-copy counts are correctly 0 for `fake_native`. `thin_view_count` is 0, consistent with no GPU thin-view path being exercised.

**Claim Boundary**

Multiply enforced and comprehensive. All 8 claim flags are `False` in four separate locations: manifest, top-level payload, per-record, and the preflight MD. The boundary text explicitly names every prohibited extension: performance claims, public speedup, whole-app speedup, broad RTX wording, true zero-copy, COLLECT_K_BOUNDED promotion, partner tensor handoff, package install claims, release tags, and release action. `timing_recorded_for_diagnostics_only: true` is a validated field, not advisory text.

**Fail-Closed Validation**

`validate_record()` uses identity checks (`is not True`) for boolean guards, preventing truthy-but-not-True values from bypassing checks. Required metadata fields are enumerated and presence-checked on every record before any claim or comparison field is examined. The function raises `ValueError` — not returns a flag — on any violation. `main()` propagates a non-zero exit code if `accepted` is false, making CI behavior fail-closed. `run_fake_prepared_host_output_case()` calls `validate_record()` before returning, so no unvalidated record can escape.

**Test Adequacy**

Five tests covering: schema reuse and claim-flag closure (positive), integration smoke with pinned counter values (positive), claim-flag expansion rejection and missing `path_comparison` (negative), and three distinct path-comparison regressions — negative delta, diagnostic-flag cleared, buffer-reuse cleared (negative). All five named negative scenarios from the prompt are present with specific `assertRaisesRegex` matchers. The foundation-report test also guards the human-readable scope statement.

**Artifact Consistency**

JSON artifact: `git_commit` prefix `22852c5e` matches HEAD. `candidate_row_count: 256` = 64 × 4. `baseline_input_materialization_count: 5`, `prepared: 1`, `delta: 4` — correct for `iterations=5`. `prepared_host_output_buffer_reused: true`, `stable_typed_input_buffer_address: true`, `timing_recorded_for_diagnostics_only: true`. All consistent with the script logic.

**Minor observations (non-blocking)**

- `_output_buffer(capacity)` returns `None` for `capacity <= 0` (`script:86–87`). This path is unreachable since `build_candidate_rows` validates `unique_rows > 0`. Harmless dead code.
- `output_materialization_sec` and `validation_sec` are hardcoded `0.0`. Correct for `fake_native` — no GPU output materialization or on-device validation occurs.

---

### Required Fixes

None.

---

### Acceptance Notes

- This preflight authorizes **schema compatibility and measurement-plumbing validation only**, using a deterministic fake native symbol.
- It is **not** Embree or OptiX performance evidence.
- It is **not** public speedup evidence of any kind.
- Timing figures in the JSON artifact are diagnostic values from a single local Windows 10 machine and must not be cited as performance benchmarks.
- Promotion of `COLLECT_K_BOUNDED`, release tags, and release action all remain blocked pending separate reviewed evidence.
- Real backend runs must use this runner shape and keep the same claim boundary until a separate review explicitly narrows it.
