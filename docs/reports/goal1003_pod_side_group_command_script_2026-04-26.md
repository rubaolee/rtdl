# Goal1003 Pod-Side Group Command Script

Date: 2026-04-26

## Scope

Add a current pod-side shell helper for the next paid RTX session so execution
uses the same OOM-safe A-H group structure as the refreshed Goal962 packet and
`docs/rtx_cloud_single_session_runbook.md`.

## Changes

- Added `scripts/goal1003_rtx_pod_group_commands.sh`.
- The script:
  - assumes an already-running RTX-class Linux pod and an RTDL checkout;
  - does not create cloud resources;
  - does not contain credentials;
  - checks `nvidia-smi`, `nvcc`, and `OPTIX_PREFIX/include/optix.h`;
  - runs Goal763 bootstrap first;
  - runs Goal761 groups A-H one at a time;
  - prints a copy-back reminder before pod shutdown.
- Added `tests/goal1003_rtx_pod_group_commands_test.py` to pin the helper's
  boundary and group targets.

## Verification

Commands run:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1003_rtx_pod_group_commands_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal962_next_rtx_pod_execution_packet_test
bash -n scripts/goal1003_rtx_pod_group_commands.sh
git diff --check
```

Result: `Ran 16 tests`, `OK`; shell syntax check passed.

## Boundary

This is an execution helper for a pod that already exists. It does not start,
stop, rent, or provision cloud resources, and it does not authorize public RTX
speedup claims.
