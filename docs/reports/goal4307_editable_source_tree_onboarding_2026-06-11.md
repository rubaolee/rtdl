# Goal4307: Editable Source-Tree Onboarding

Date: 2026-06-11

## Verdict

`accept-with-boundary` for the first Fable5 P7 learner-onboarding slice.

Goal4307 adds a minimal local editable source-tree path so learners and
developers can import `rtdsl` without setting `PYTHONPATH` in every shell. This
addresses the review finding that the first-run experience looked too much like
a lab checkout.

## What Changed

- Added `pyproject.toml` with the local distribution name `rtdl-source-tree`.
- The editable metadata exposes only `src/rtdsl*`.
- `scripts/rtdl_source_tree_doctor.py` now reports the optional editable
  source-tree metadata as a non-required check.
- `README.md`, `docs/learn/source_tree_doctor.md`, and the current first-run
  tutorials document two source-checkout paths:
  - `PYTHONPATH=src:.`
  - `python -m pip install -e .`

## Boundary

This is not a package-install claim. It does not say RTDL is available from
PyPI, does not create a wheel release, and does not authorize public package
installation wording.

The editable path only makes the current checkout importable as `rtdsl` in the
active Python environment.

Goal4307 does not authorize:

- release action,
- package-install wording,
- public speedup wording,
- whole-app acceleration wording,
- broad RT-core wording,
- true-zero-copy wording,
- automatic partner selection,
- paper reproduction claims,
- app-specific native-engine logic.

## Validation

Focused validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4307_editable_source_tree_onboarding_test tests.goal4306_partner_column_contracts_foundation_test tests.goal4303_current_security_redaction_guard_test tests.goal4305_fable5_evidence_and_process_docs_test

Ran 13 tests in 0.353s
OK (skipped=1)
```

Editable metadata dry-run from the initial Goal4307 pass:

```text
py -3 -m pip install -e . --no-deps --dry-run

Would install rtdl-source-tree with the then-current v2.10 metadata
```

Goal4309 follow-up: Claude flagged that the v2.10 metadata was confusing while the active
work is in the v2.11 lane. `pyproject.toml` now declares
`rtdl-source-tree` version `2.11.0`. The Windows `py -3 -m pip` launcher in
this shell is currently missing `pip`, so the follow-up validation uses the
source-tree doctor and the `pyproject.toml` parser test rather than claiming a
fresh pip dry-run.

Local Linux focused validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal4307_editable_source_tree_onboarding_test tests.goal4306_partner_column_contracts_foundation_test tests.goal4305_fable5_evidence_and_process_docs_test tests.goal4303_current_security_redaction_guard_test tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4299_numba_topk_partner_reference_test

Ran 22 tests in 0.851s
OK
```

The test checks:

- `pyproject.toml` is source-tree editable metadata for `rtdsl*`,
- the doctor reports editable metadata as optional,
- public docs include the optional editable command,
- public docs keep the package-claim boundary explicit.

## Remaining Work

This goal does not remove every example's defensive source-tree bootstrap. That
can be done incrementally after more users follow the editable path. The safe
next step is to update learner-facing examples first, leaving benchmark scripts
unchanged until their pod runner entrypoints are revalidated.
