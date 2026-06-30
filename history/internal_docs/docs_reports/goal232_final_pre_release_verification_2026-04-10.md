# Goal 232 Report: Final Pre-Release Verification

Date: 2026-04-10
Status: implemented

## Summary

This goal runs the final local verification package in the clean
release-prep worktree so the `v0.4` release path stands on current evidence,
not only on earlier audit snapshots.

## Workspace

- clean worktree:
  - `/Users/rl2025/worktrees/rtdl_v0_4_release_prep`
- branch:
  - `codex/v0_4_release_prep`

## Verification Command

- `PYTHONPATH=src:. python3 scripts/run_full_verification.py`

## Verification Result

The full verification package passed.

Unittest discover slice:

- command:
  - `/opt/homebrew/opt/python@3.14/bin/python3.14 -m unittest discover -s tests -p '*_test.py'`
- result:
  - `Ran 525 tests in 116.882s`
  - `OK (skipped=59)`

CLI smoke results:

- `baseline_runner_missing_arg`
  - return code `2`
- `baseline_runner_invalid_dataset`
  - return code `1`
- `baseline_runner_cpu`
  - returned `2` rows

Artifact smoke results:

- evaluation artifacts created:
  - `csv`
  - `gap_analysis`
  - `json`
  - `latency_svg`
  - `markdown`
  - `pdf`
  - `scaling_svg`
  - `speedup_svg`
- Goal 15 compare smoke:
  - `lsi_pairs = 24000`
  - `pip_pairs = 120`

Embree smoke:

- not skipped
- parity `true`
- CPU rows `2`

## Relationship To Earlier Evidence

This verification does not replace the earlier whole-line audits, heavy Linux
benchmark, or Goal 229 boundary-fix evidence. It complements them:

- Goal 212 whole-line audit package remains preserved
- Goal 228 heavy Linux benchmark remains preserved
- Goal 229 accelerated boundary-fix evidence remains preserved

Together, these now form the final pre-release evidence package in the clean
release-prep worktree.

## Outcome

`v0.4` is technically ready for a final release decision in this clean
worktree.

That still does **not** authorize:

- `VERSION` bumping
- tag creation
- release declaration

Those remain explicit user-authorized steps.
