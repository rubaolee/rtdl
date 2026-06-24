# Goal4289: Remote Pod Driver Streaming Fix

Date: 2026-06-11

## Trigger

Goal4287 Claude review accepted the Goal4286 remote pod driver only with a
boundary: execute mode used `subprocess.run(..., stdout=PIPE, stderr=PIPE)`.
That buffered all pod progress until the SSH process exited, defeating the
purpose of visible progress markers for long hardware sessions.

## Fix

`scripts/rtdl_remote_pod_validation_driver.py` now uses `subprocess.Popen` for
execute mode and streams combined remote output line by line.

- In normal execute mode, remote progress is written to stdout as it arrives.
- In `--json` execute mode, remote progress is written to stderr so the final
  JSON summary remains parseable on stdout.
- A timer kills the SSH process after `--timeout-sec`.
- The final summary records `timed_out`, `returncode`, and the output tail.
- Dry-run JSON now records `timeout_sec`.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal4286_remote_pod_validation_driver_test `
  tests.goal4289_remote_pod_driver_streaming_fix_test
```

The broader v2.10 release-hardening gate includes these tests plus the existing
claim-scan, doctor, probe, bundle, evidence-index, tutorial, doc, release-packet,
and consensus tests.

## Boundary

This is an execution-tool fix only. It does not run pod hardware validation,
move tags, install packages, or authorize package-install, broad RT-core,
whole-application speedup, or release claims.

## Verdict

`accept`: the live pod driver can now show progress during long SSH runs instead
of silently buffering until process exit.
