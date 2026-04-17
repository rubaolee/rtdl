# Response To v0.7 DB Expert Attack Suite Audit

Date: 2026-04-17

External input:

- `/Users/rl2025/antigravity-working/rtdl-4-16/docs/reports/v0_7_db_expert_attack_suite_audit_comprehensive_2026-04-17.md`

Preserved local copy:

- `/Users/rl2025/rtdl_python_only/docs/reports/v0_7_db_expert_attack_suite_audit_comprehensive_2026-04-17.md`

## Verdict

`ACCEPT WITH CORRECTION`.

The external audit is useful and confirms the direction of the v0.7 DB attack
suite, but two claims needed local correction:

- The report says four critical bugs were fixed, but it describes three fixed
  issue classes and one unresolved empty-table issue.
- The report says empty-table handling remains unresolved, but the current local
  repo already includes the Goal 469 empty-table fast path for native CPU DB
  workloads.

The local response also found one real remaining consistency gap behind the
report's "error surface consistency" claim: missing grouped fields could still
surface as `KeyError` in some reference/preprocessing paths. That has now been
fixed.

## Local Verification Against Current Repo

The following already existed before this response:

- `/Users/rl2025/rtdl_python_only/tests/test_v07_db_attack.py`
- `/Users/rl2025/rtdl_python_only/tests/goal469_v0_7_db_attack_gap_closure_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal469_v0_7_db_attack_report_gap_closure_2026-04-16.md`

Goal 469 already closed the native CPU empty-table edge case by returning `()`
before the C ABI needs schema information:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

## New Remediation In This Response

Changed:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/db_reference.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py`
- `/Users/rl2025/rtdl_python_only/tests/test_v07_db_attack.py`

Fixes:

- `grouped_count_cpu` now raises `ValueError` for missing group-key fields
  instead of leaking `KeyError`.
- `grouped_sum_cpu` now raises `ValueError` for missing group-key or sum-value
  fields instead of leaking `KeyError`.
- native DB text-field preprocessing now raises `ValueError` when a required
  predicate/group field is absent from any row.
- attack-suite assertions now require `ValueError`; they no longer accept
  `KeyError` for missing predicate, group, or value fields.

## Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.test_v07_db_attack tests.goal469_v0_7_db_attack_gap_closure_test -v
```

Result:

```text
Ran 114 tests in 2.806s
OK
```

Whitespace check:

```text
git diff --check
```

Result:

```text
OK
```

## Corrected Interpretation Of External Report

Accepted evidence:

- The external report is a valid additional audit artifact for v0.7 DB kernels.
- It reinforces the importance of `conjunctive_scan`, `grouped_count`, and
  `grouped_sum` stress coverage.
- It correctly identifies operand-order, platform build, error-surface, and
  empty-input behavior as high-priority DB hardening areas.

Corrections:

- Do not repeat the phrase "four critical bug fixes" unless the fourth fix is
  separately identified and linked to a concrete local patch.
- Do not describe empty-table handling as unresolved for the current local
  native CPU path; Goal 469 already fixed it and this response re-ran the
  relevant regression tests.
- Do not use "Production Stable" without qualifying the backend and evidence
  boundary. The honest statement is: the v0.7 bounded DB surface is
  regression-tested for the local CPU/reference path here, with broader
  backend/platform evidence preserved in the v0.7 release reports.

## Remaining Boundary

This response did not run Linux PostgreSQL, OptiX, Vulkan, or large remote
backend tests. Those remain separate Linux-host validation gates. This response
is a local intake and correctness-hardening pass for the newly supplied external
audit report.
