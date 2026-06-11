# Goal4291: Remote Pod Driver Noninteractive SSH

Date: 2026-06-11

## Trigger

The first live attempt against pod `root@194.68.245.114:22158` started the local
driver, Python, and SSH processes but produced no remote progress lines. The
likely cause was SSH waiting before remote script execution, such as a host-key
prompt.

## Fix

`scripts/rtdl_remote_pod_validation_driver.py` now builds SSH commands with
noninteractive pod-safe options:

- `BatchMode=yes`
- `StrictHostKeyChecking=accept-new`
- `ConnectTimeout=20`
- `ServerAliveInterval=30`
- `ServerAliveCountMax=4`
- `LogLevel=ERROR`

This lets ephemeral pod host keys be accepted automatically while still failing
closed for password/passphrase prompts and connection failures.

## Boundary

This only hardens the remote driver. It does not run hardware validation by itself,
install packages, move tags, or authorize release/performance claims.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4286_remote_pod_validation_driver_test
```

The next live pod attempt should use the same driver command and should show
`[rtdl-remote-pod]` progress lines shortly after launch.

## Verdict

`accept`: the driver no longer allows a hidden SSH host-key prompt to silently
consume pod time before any remote progress appears.
