# Goal4285: Pod Probe Generic OptiX Candidate

Date: 2026-06-11

## Purpose

Close the non-blocking Goal4282 Claude review note that the v2.10 pod
bootstrap probe still mentioned a developer-specific OptiX SDK path:
`/home/lestat/vendor/optix-dev`.

The probe is meant to be a generic pod and workstation preflight tool. It
should support local developer machines without making the public runbook look
tied to one account name.

## Change

- Replaced the hard-coded `/home/lestat/vendor/optix-dev` candidate with
  `Path.home() / "vendor" / "optix-dev"`.
- Added generic workspace candidates:
  - `/workspace/vendor/optix-sdk`
  - `/workspace/vendor/optix-dev`
- Kept the established pod candidates:
  - `OPTIX_PREFIX`
  - `/root/vendor/optix-sdk`
  - `/root/vendor/optix-dev`
  - `/workspace/vendor/optix-dev-8.0.0`
- Deduplicated candidate paths before probing them.
- Updated the pod bootstrap runbook to document `$HOME/vendor/optix-dev`
  rather than a local user path.

## Boundary

This does not install OptiX, build `librtdl_optix`, run hardware timing, move a
release tag, or authorize any performance claim. It only makes the preflight
candidate list more portable.

## Validation

Focused validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal4281_pod_bootstrap_probe_test `
  tests.goal4285_pod_probe_generic_optix_candidate_test
```

The broader v2.10 release-hardening gate should continue to include the
Goal4281 probe test and Goal4280 bundle test.

## Verdict

`accept`: the review nit is closed in code, docs, and regression tests while
preserving the non-authorizing pod preflight boundary.
