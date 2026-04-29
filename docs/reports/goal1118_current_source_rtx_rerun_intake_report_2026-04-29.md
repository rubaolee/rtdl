# Goal1118 Current-Source RTX Rerun Intake Report

Date: 2026-04-29

## Verdict

ACCEPT as a pre-cloud/post-cloud gate. Goal1118 adds an intake tool for the
Goal1116 current-source RTX rerun packet.

The current default intake output is intentionally `valid: false` because the
pod artifacts have not been collected yet.

## What The Intake Checks

- All five expected Goal1116 output JSON files exist.
- `goal1116_runner.log` exists.
- Every artifact records a non-empty `source_commit`.
- All artifacts share one source commit.
- All artifacts report `optix` mode.
- Validation rows match the CPU/oracle reference.
- Timing rows do not claim oracle parity when they use `--skip-validation`.
- Timing rows meet their configured median query timing floor.
- Public speedup claim authorization remains false.

## Generated Artifacts

- `scripts/goal1118_current_source_rtx_rerun_intake.py`
- `tests/goal1118_current_source_rtx_rerun_intake_test.py`
- `docs/reports/goal1118_current_source_rtx_rerun_intake_2026-04-29.json`
- `docs/reports/goal1118_current_source_rtx_rerun_intake_2026-04-29.md`

## Local Default Status

The local default status is blocked pending pod execution:

| Metric | Value |
|---|---:|
| Expected rows | 5 |
| Valid rows | 0 |
| Missing rows | 5 |
| Runner log exists | false |
| Public speedup claim authorized | false |

## Verification

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal1118_current_source_rtx_rerun_intake_test -v
```

Result: 4 tests OK.

Command:

```text
PYTHONPATH=src:. python3 scripts/goal1118_current_source_rtx_rerun_intake.py || true
```

Result: generated an honest blocked report because no pod artifacts are present.

## Boundary

This goal does not run cloud, does not authorize release, does not change public
wording, and does not authorize public RTX speedup claims.
