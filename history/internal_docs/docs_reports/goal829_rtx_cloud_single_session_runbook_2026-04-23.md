# Goal829 RTX Cloud Single-Session Runbook

Date: 2026-04-23

## Purpose

Goal829 adds an operator-facing runbook for the next paid NVIDIA RTX cloud
session. The goal is to prevent repeated cloud pod start/stop loops by requiring
local readiness first and then using one batched pod command.

## Added Files

- `/Users/rl2025/rtdl_python_only/docs/rtx_cloud_single_session_runbook.md`
- `/Users/rl2025/rtdl_python_only/tests/goal829_rtx_cloud_single_session_runbook_test.py`

## Runbook Contents

The runbook records:

- Local pre-pod gate: `scripts/goal824_pre_cloud_rtx_readiness_gate.py`.
- Accepted condition: `"valid": true`.
- One-shot cloud command: `scripts/goal769_rtx_pod_one_shot.py`.
- Optional deferred batching with `--include-deferred` and repeated `--only`.
- Required artifact contract checks from Goal827.
- Files to copy back.
- Shutdown rule after artifacts are copied.
- Explicit non-authorization of public RTX speedup claims.

## Cloud Cost Policy

No pod was started. This goal improves the procedure before the next paid run.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal829_rtx_cloud_single_session_runbook_test
```

Result:

```text
Ran 3 tests
OK
```

## Verdict

Goal829 is complete locally. The next cloud use should be a single batched
session, not a per-app restart/stop cycle.
