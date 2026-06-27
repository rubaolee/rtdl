# Goal4290: Remote Pod Driver Ref Pinning

Date: 2026-06-11

## Purpose

Close the Goal4287 review recommendation to avoid an implicit "whatever is on
`main` at clone time" pod run. The remote driver now exposes the repository URL
and ref in its dry-run JSON and generated remote script.

## Change

- Added `--repo-url`, defaulting to `https://github.com/rubaolee/rtdl.git`.
- Added `--ref`, defaulting to `main`.
- Dry-run JSON now records `repo_url` and `ref`.
- The generated remote script clones the requested repo and, for non-`main`
  refs, fetches the requested ref and checks out `FETCH_HEAD` detached.
- Updated the remote driver runbook with `--ref main` examples and the
  `--repo-url` / `--ref` override guidance.

## Boundary

This makes pod execution more reproducible; it does not move tags, create a
release, run hardware validation, or authorize performance claims.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal4286_remote_pod_validation_driver_test `
  tests.goal4290_remote_pod_driver_ref_pinning_test
```

## Verdict

`accept`: the remote pod driver can now show exactly which repo and ref it will
run before `--execute` is used.
