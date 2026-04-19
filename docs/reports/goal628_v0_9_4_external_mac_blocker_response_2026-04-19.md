# Goal 628: v0.9.4 External macOS Blocker Response

Date: 2026-04-19

Repository: `/Users/rl2025/rtdl_python_only`

## Input

An external tester re-ran the v0.9.4 release suite after the stale Goal532
version assertion was fixed and still reported `BLOCK` for two remaining
classes:

1. Optional native C++ comparison tests failed with `CalledProcessError` when
   local macOS GEOS/Embree linker paths were unavailable or incompatible.
2. `goal207_knn_rows_external_baselines_test` failed on a last-bit float
   difference: `1.9673477671728574` vs `1.967347767172857`.

The external report artifact is:

- `/Users/rl2025/rtdl_python_only/docs/reports/external_v0_9_4_release_level_test_report_2026-04-19.md`

## Root Cause

The external report is correct that these should not be hard failures in a
portable release-level Python test suite.

The optional native comparison tests are useful when a local native toolchain is
complete, but they depend on host-specific C++ linkability for Embree and GEOS.
If that optional toolchain is missing, the test should skip with an explicit
reason instead of failing the whole suite.

The KNN external baseline test compared floating-point rows with exact
dictionary equality. That is too strict for independently computed distances
when the row identity and rank are identical and the difference is below normal
floating-point tolerance.

## Fix

Added:

- `/Users/rl2025/rtdl_python_only/tests/_optional_native_compare.py`

Updated:

- `/Users/rl2025/rtdl_python_only/tests/goal15_compare_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal17_prepared_runtime_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal19_compare_test.py`
- `/Users/rl2025/rtdl_python_only/tests/report_smoke_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal207_knn_rows_external_baselines_test.py`

Behavior after the fix:

- Optional native comparison build/link failures containing GEOS, Embree,
  `pkg-config`, missing library, or non-zero compile/link markers now become
  `SkipTest` in the affected optional native comparison tests.
- Real comparison mismatches still fail because only build/link/toolchain
  availability failures are converted to skips.
- KNN external-baseline tests compare `query_id`, `neighbor_id`, and
  `neighbor_rank` exactly, while comparing `distance` with `assertAlmostEqual`
  at 12 decimal places.

## Validation

Focused blocker set:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal15_compare_test \
  tests.goal17_prepared_runtime_test \
  tests.goal19_compare_test \
  tests.report_smoke_test \
  tests.goal207_knn_rows_external_baselines_test -v
```

Result:

```text
Ran 20 tests in 30.946s
OK
```

Full local release suite:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Result:

```text
Ran 1178 tests in 108.192s
OK (skipped=171)
```

Public-doc focused checks:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal512_public_doc_smoke_audit_test \
  tests.goal531_v0_8_release_candidate_public_links_test \
  tests.goal515_public_command_truth_audit_test -v
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```text
Ran 7 tests in 0.021s
OK
```

Command truth audit:

```json
{"command_count": 244, "public_doc_count": 14, "valid": true}
```

Diff hygiene:

```bash
git diff --check
```

Result: clean.

## Verdict

ACCEPT pending external AI review.

The two reported blocker classes have been addressed without weakening
correctness requirements:

- optional native dependency absence is skipped only for optional native
  comparison tests
- true backend row mismatches still fail
- KNN distance comparisons now use an appropriate numeric tolerance while
  preserving exact row identity and rank checks
