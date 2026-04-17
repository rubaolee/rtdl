# Goal 500 External Review — v0.7 DB Expert Attack Suite Audit Response

**Date**: 2026-04-17
**Reviewer**: Claude (claude-sonnet-4-6)
**Verdict**: ACCEPT

---

## Review Criteria

### 1. External Input Preserved Correctly — PASS

The response document correctly captures the external report path, stores a local copy, and clearly distinguishes what it accepts versus what it corrects. The two corrections are accurate and well-reasoned:

- "Four critical bugs" is an overclaim; the external report describes three fixed classes and one open item. The response flags this without dismissing the audit.
- "Unresolved empty-table handling" is stale relative to the current repo; Goal 469 already fixed the native CPU path. The response cites the prior work and re-runs its regression tests rather than re-doing the work.

### 2. Error-Contract Gap Fixed — PASS

The diffs close the gap cleanly in all three affected paths:

**`db_reference.py`**: `grouped_count_cpu` and `grouped_sum_cpu` now call `_require_row_field()` for every group key and sum-value field access. The new helper raises `ValueError` with a descriptive message. Previously both functions used raw `row[field]` which silently leaked `KeyError`.

**`oracle_runtime.py`**: `_encode_db_text_fields` now validates all required fields are present in every row (raising `ValueError`) before the encoding loop. The old `if field in row` guard in the list comprehension was silently swallowing missing-field rows; that guard has been removed, so encoding is now total and consistent.

**`tests/test_v07_db_attack.py`**: Three existing tests tightened from `(ValueError, KeyError)` to `ValueError`. Two new `TestDbReferenceCpuDirect` tests cover missing group-key and missing value-field paths on the reference functions directly. One new integration-level test covers missing group-key through the oracle path.

No overclaiming: the fix scope is precisely the error-surface consistency issue identified in Bug #3 of the external report. Operand-order and Darwin build fixes from the external report are not re-litigated here because they predate this response; that boundary is stated clearly.

### 3. Release Stability Not Overclaimed — PASS

The response explicitly rejects the "Production Stable" language from the external report and replaces it with a qualified statement: the v0.7 bounded DB surface is regression-tested for the local CPU/reference path, with broader backend/platform evidence in the prior release reports. The "Remaining Boundary" section lists what was not run (Linux, PostgreSQL, OptiX, Vulkan, large remote backends). This is the correct epistemic posture for a local intake pass.

---

## Summary

All three review criteria pass. The code changes are minimal, targeted, and internally consistent. The test coverage improvement is real: new test cases exercise previously uncovered code paths. The response document handles the external artifact with appropriate skepticism — accepting the signal, correcting the overclaims, and scoping its own work honestly.

**ACCEPT**
