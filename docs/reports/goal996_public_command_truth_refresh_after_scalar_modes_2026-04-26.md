# Goal996 Public Command Truth Refresh After Scalar Modes

Date: 2026-04-26

## Scope

Refresh the public command truth audit after Goal992/Goal993/Goal994/Goal995
changed claim-facing fixed-radius commands to explicit scalar modes:

- Outlier: `--output-mode density_count`
- DBSCAN: `--output-mode core_count`

## Changes

- Added exact command coverage keys for the Goal992 scalar fixed-radius app
  commands in `scripts/goal515_public_command_truth_audit.py`.
- Tightened Markdown table parsing so normalized commands stop at the closing
  backtick instead of carrying trailing table cells into the command string.
- Updated `tests/goal515_public_command_truth_audit_test.py` to require:
  - `goal992_scalar_fixed_radius_command_exact`
  - exact outlier `density_count` command
  - exact DBSCAN `core_count` command
- Regenerated:
  - `docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
  - `docs/reports/goal515_public_command_truth_audit_2026-04-17.md`

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result summary:

```json
{
  "valid": true,
  "public_doc_count": 15,
  "command_count": 296,
  "coverage_counts": {
    "goal992_scalar_fixed_radius_command_exact": 4
  }
}
```

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal515_public_command_truth_audit_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal938_public_rtx_wording_sync_test
```

Result: `Ran 7 tests in 0.017s`, `OK`.

Additional checks:

```bash
python3 -m py_compile scripts/goal515_public_command_truth_audit.py
git diff --check
```

Results: passed.

## Boundary

This goal refreshes command-audit coverage and generated audit artifacts only.
It does not execute GPU commands, does not change backend kernels, and does not
authorize public RTX speedup claims.
