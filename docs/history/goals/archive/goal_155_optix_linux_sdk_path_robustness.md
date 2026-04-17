# Goal 155: OptiX Linux SDK Path Robustness

## Why

An external Antigravity user-style test report excluded OptiX from its Linux
run because it reasonably inferred that the required native OptiX dependency
was missing on that host.

Follow-up investigation showed the host already had a usable OptiX SDK, but
RTDL was not discovering it because the Makefile assumed `/opt/optix` while the
real host installation was elsewhere.

That is still a real product robustness problem:

- the host already had a usable OptiX SDK
- RTDL still failed because its default path assumption was too narrow

## Scope

- inspect the external OptiX failure report
- inspect the real Linux host SDK layout
- fix the Makefile so `make build-optix` can find common SDK roots
- add a clearer preflight failure message when the SDK is still missing
- validate real Linux OptiX build success after the fix

## Acceptance

- `make build-optix` succeeds on `lestat@192.168.1.20` without a manual
  `OPTIX_PREFIX` override
- the Makefile now auto-detects the actual Linux host SDK location
- missing-SDK failures now tell the user how to fix the problem
- the package is reviewed before it is treated as online
