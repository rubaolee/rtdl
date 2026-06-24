---

## Verdict

**ACCEPTED** as a local phase/copy measurement foundation for v1.6.1. No blocking issues found. All five artifacts are internally consistent and correctly scoped.

---

## Findings

### Schema and validation (script)

- All 12 `PHASE_FIELDS` and 7 `COPY_COUNT_FIELDS` are defined, enforced by `validate_record`, and present in the smoke JSON (nulls allowed where a CPU-reference smoke can't observe them — documented and correct).
- All 8 `CLAIM_FLAGS` default to `False`. The validator uses `is not False` (identity, not equality), which correctly rejects truthy non-booleans. Good.
- `run_case` (line 222) and `run_package` (line 274) both write `dict(CLAIM_FLAGS)` — copies, not references to the module-level dict. Mutation cannot silently propagate. ✓
- `_normalize_phases` always overwrites `total_wrapper_sec` from the wall-clock wrapper timer, ignoring any app-reported value of the same name. Intentional and correct.
- `validate_record` iterates `flags.items()` (not just `CLAIM_FLAGS` keys) on the false-value check. This means any extra flag sneaked into a record also gets rejected. Stricter than needed but safe.

### Test file

- Five test methods covering: manifest shape, live smoke run, markdown/JSON scope assertions, rejection of negative phases and mutated flags, and foundation report presence.
- The reported "18 tests, OK" is the full suite count; the 5 methods here are a subset. No gap — the file doesn't claim to be the entire suite.
- `test_local_smoke_package_records_complete_phase_and_copy_shape` hard-codes `input_materialization_count == 4`, `python_row_count == 4`, `output_materialization_count == 4`. This matches the smoke JSON and is appropriate for a fixed smoke fixture.

### Smoke JSON/MD artifacts

- All required top-level keys present: `status`, `accepted`, `goal`, `version_slot`, `claim_flags`, `claim_boundary`, `manifest`, `records`.
- Record-level `claim_flags`: all 8 flags present, all `false`. ✓
- `phase_times_sec`: all 12 fields present (5 observed, 7 null — CPU-reference limitation). ✓
- `copy_counts`: all 7 fields present (3 observed, 4 null). ✓
- `status: "pass"` and `returncode: 0`. ✓
- `stdout_excerpt` is truncated at 1000 chars (the raw string is cut mid-sentence); this is the configured behaviour and the normalized fields hold the actual data. No information loss in the validated fields.

### Foundation report

All four strings required by `test_foundation_report_is_present_and_names_default_artifacts` are present. Claim boundary section is explicit, matching the JSON verbatim.

---

## Required Fixes

None. No blocking defects.

---

## Acceptance Notes

- **Scope is correctly narrow.** This is a schema/measurement-harness commit only. No speedup numbers, no RTX claims, no release gating — all eight `claim_flags` are explicitly false in every artifact and enforced by the validator.
- **Three minor observations for the log (non-blocking):**
  1. `_extract_json`'s brace-scan fallback could silently accept the first `{...}` in stdout if the app ever emits non-JSON preamble. Acceptable for a local smoke runner; worth a comment if the runner is extended to less-controlled apps.
  2. The app-reported `"copies": 1` field in stdout is not mapped to any copy-count slot. If "copies" has a distinct meaning from the seven defined fields, that's fine; if it should map to one of them, the next goal should clarify.
  3. The `validate_record` extra-flag check (iterating all `flags.items()`) goes slightly beyond "check CLAIM_FLAGS membership" — it is stricter, not weaker, so no correctness concern.
- **ACCEPTED** for its stated purpose: establishing the v1.6.1 phase/copy measurement schema and producing a reproducible local smoke record before optimization or pod work begins.
