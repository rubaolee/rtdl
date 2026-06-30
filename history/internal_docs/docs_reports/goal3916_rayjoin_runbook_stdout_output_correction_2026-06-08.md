# Goal3916 RayJoin Runbook Stdout Output Correction

Date: 2026-06-08

## Purpose

Goal3913 introduced a safe next-pod runbook for the RayJoin representative profile. A dry-run smoke found that `scripts/goal3866_rayjoin_representative_scale_profile.py` does not accept `--output`; it writes JSON to stdout. Goal3916 corrects the runbook before any fresh pod run uses it.

## Change

The runbook now redirects:

- stdout to `/root/goal3913_rayjoin_subprobe_artifacts/summary.json`;
- stderr/progress logs to `/root/goal3913_rayjoin_subprobe_artifacts/run.log`.

The regression test now asserts that the runbook does not contain the invalid `--output /root/goal3913_rayjoin_subprobe_artifacts/summary.json` argument.

## Validation

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3913_safe_next_pod_rayjoin_runbook_test
```

Expected result: all tests pass.
