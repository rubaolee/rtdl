# Goal4292: Remote Pod Driver LF Pipe Fix

Date: 2026-06-11

## Trigger

After switching to the working RTDL pod key, the remote driver reached the pod
but failed immediately:

```text
bash: line 1: set: pipefail
: invalid option name
```

That indicates Windows text-mode pipe translation sent CRLF newlines to
`bash -s`, so bash saw `pipefail\r`.

## Fix

`scripts/rtdl_remote_pod_validation_driver.py` now writes the generated remote
script as UTF-8 bytes to SSH stdin and decodes stdout bytes while streaming.
This avoids Windows text-mode newline conversion and preserves LF-only shell
input for Linux pods.

## Boundary

This only fixes the remote execution transport. It does not run hardware
validation by itself, install dependencies, move tags, or authorize any
release/performance claim.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal4286_remote_pod_validation_driver_test `
  tests.goal4292_remote_pod_driver_lf_pipe_fix_test
```

## Verdict

`accept`: the driver no longer relies on Windows text-mode stdin for a Linux
shell script.
